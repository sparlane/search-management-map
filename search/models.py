"""
Models for types of searches

Each search type has a model to represent it,
all inherting from the abstract model (SearchPath)
"""
import math

from django.db import models, connection as dbconn
from django.db.models import Func
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, LineString
from django.utils import timezone

from data.models import GeoTime, GeoTimeLabel
from assets.models import AssetType, Asset
from search.polygon.convex import creep_line_concave as polygon_creep_line
from search.polygon.convex import conv_lonlat_to_meters, conv_meters_to_lonlat
from timeline.helpers import timeline_record_search_queue


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class SearchParams():
    """
    Basic parameters for a search
    """
    def __init__(self, from_geo, asset_type, creator, sweep_width):
        self._from_geo = from_geo
        if not isinstance(asset_type, AssetType):
            raise TypeError("asset_type is not an AssetType")
        self._asset_type = asset_type
        if not isinstance(creator, get_user_model()):
            raise TypeError("creator is not a User")
        self._creator = creator
        self._sweep_width = int(sweep_width)
        if self._sweep_width < 0:
            raise ValueError("Sweep width must be positive")

    def from_geo(self):
        """
        Return the base user geometry used as a reference for the search
        """
        return self._from_geo

    def asset_type(self):
        """
        Return the asset type that this search applies to
        """
        return self._asset_type

    def creator(self):
        """
        Return the user who is creating this search
        """
        return self._creator

    def sweep_width(self):
        """
        Return the sweep width in meters for this search
        """
        return self._sweep_width


class FirstPointDistance(Func):
    """
    Calculates the distance from a given point to the first point on the search line
    """
    # pylint: disable=W0223
    function = 'ST_Distance'

    def as_sql(self, compiler, connection, function=None, template=None, arg_joiner=None, **extra_context):
        point_sql = "'SRID=4326;POINT({} {})'::geography".format(self.extra['point'].y, self.extra['point'].x)
        return super().as_sql(compiler, connection, function='ST_Distance', template="%(function)s(ST_PointN(line::geometry,1)::geography, " + point_sql + ")",
                              arg_joiner=arg_joiner, extra_context=extra_context)


class SearchPath(GeoTime):
    """
    An abstract model that presents a search.

    Common parameters are set in this model,
    and it inherits from a model that represents the path.
    """
    created_for = models.ForeignKey(AssetType, on_delete=models.PROTECT)
    sweep_width = models.IntegerField()
    inprogress_by = models.ForeignKey(Asset, on_delete=models.PROTECT, null=True, blank=True, related_name='inprogress_by%(app_label)s_%(class)s_related')
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(Asset, on_delete=models.PROTECT, null=True, blank=True, related_name='completed_by%(app_label)s_%(class)s_related')

    queued_at = models.DateTimeField(null=True, blank=True)
    queued_for_assettype = models.ForeignKey(AssetType, on_delete=models.PROTECT, null=True, blank=True, related_name='queued_for_assettype%(app_label)s_%(class)s_related')
    queued_for_asset = models.ForeignKey(Asset, on_delete=models.PROTECT, null=True, blank=True, related_name='queued_for_assettype%(app_label)s_%(class)s_related')

    datum = models.ForeignKey(GeoTimeLabel, on_delete=models.PROTECT)

    def distance_from(self, point):
        """
        Calculate the distance (in m) from a point to the start of this search
        """
        annotated_self = self.__class__.objects.annotate(distance=FirstPointDistance('line', output_field=models.FloatField(), point=point)).get(pk=self.pk)
        return annotated_self.distance

    @classmethod
    def all_waiting(cls, mission):
        """
        Get all searches for this mission that haven't been started or deleted
        """
        return cls.all_current_incomplete(mission).filter(inprogress_by__isnull=True)

    @classmethod
    def all_current_completed(cls, mission, current_at=None):
        """
        Get all the searches that are current and completed
        """
        objects = cls.all_current(mission, current_at=current_at)
        if current_at:
            objects = objects.filter(completed_at__lt=current_at)
        else:
            objects = objects.filter(completed_at__isnull=False)
        return objects

    @classmethod
    def all_current_incomplete(cls, mission, current_at=None):
        """
        Get all the searches that are current and not yet complete
        """
        objects = cls.all_current(mission, current_at=current_at)
        if current_at:
            objects = objects.filter(completed_at__gt=current_at)
        else:
            objects = objects.filter(completed_at__isnull=True)
        return objects

    @classmethod
    def find_closest(cls, mission, asset_type, point):
        """
        Find the search with the closest starting point
        Only searches that haven't been started or deleted and are for the right asset type are considered
        """
        try:
            possibles = cls.all_waiting(mission).filter(created_for=asset_type)
            search = possibles.annotate(distance=FirstPointDistance('line', output_field=models.FloatField(), point=point)).order_by('distance')[0]
            return search
        except IndexError:
            return None

    def queue_search(self, mission_user, assettype=None, asset=None):
        '''
        Queue this search for an asset or assettype
        '''
        if self.queued_at is None:
            self.queued_at = timezone.now()
            self.queued_for_asset = asset
            self.queued_for_assettype = assettype
            self.save()
            timeline_record_search_queue(mission_user.mission, mission_user.user, self, assettype, asset)

    @classmethod
    def oldest_queued_for_asset(cls, mission, asset):
        """
        Find the oldest queued search for this asset
        Only entries that haven't already been started/deleted are considered
        """
        try:
            search = cls.all_waiting(mission).filter(queued_for_asset=asset).filter(queued_at__isnull=False).order_by('queued_at')[0]
            return search
        except IndexError:
            return None

    @classmethod
    def oldest_queued_for_asset_type(cls, mission, asset_type):
        """
        Find the oldest queued search for this asset_type
        Only entries that haven't already been used/deleted are considered
        """
        try:
            search = cls.all_waiting(mission).filter(queued_for_asset__isnull=True).filter(queued_for_assettype=asset_type).filter(queued_at__isnull=False).order_by('queued_at')[0]
            return search
        except IndexError:
            return None

    def get_match(self):
        """
        Get the match object associated with this queue entry
         - an asset, if this search is for a specific asset
         - an assettype, if this search is for any asset of a type
        """
        if self.queued_for_asset:
            return self.queued_for_asset
        return self.queued_for_assettype

    class Meta:
        abstract = True
        indexes = [
            # Indexes for both cases of all_current_of_*complete*
            models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'created_at', 'completed_at', ]),
            models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', ]),
            # Index for all_waiting
            models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', ]),
            # Index for find_closest
            models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'created_for', ]),
            # Index for oldest_queued_for_asset*
            models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'queued_for_asset', 'queued_for_assettype', ]),
        ]


class SectorSearch(SearchPath):
    """
    A sector search from a given point (datum).

    Sector searches are good for finding something when you knew it was at the datum
    very recently (with a few minutes of the search starting).
    A series of equilateral triangles with sides of length no greater than 3x sweep width.
    Each of the triangles has one point on the datum and the other 2 points on a circle
    centered on the datum.
    Each triangle starts 30 degress from the previous one, but they are run in an order
    such that (where possible) the line that connects to the datum continues to start a
    new triangle on the opposite side.
    There are 3 sets of 3 triangles that make up the full set. The first triangles have
    courses (position on clock face)
     000 (12 o'clock)
     120 (2 o'clock)
     240 (datum)
     240 (8 o'clock)
     000 (10 o'clock)
     120 (datum)
     120 (4 o'clock)
     240 (6 o'clock)
     000 (datum)
     The next set start offset 30 degrees (030, 150, 270, etc)
    """
    GEOJSON_FIELDS = ('pk', 'created_at', 'created_for', 'inprogress_by', 'sweep_width', 'queued_at', 'queued_for_asset', 'queued_for_assettype', )

    def __str__(self):
        return "Sector Search from {} with {} (sw={})".format(self.datum, self.created_for, self.sweep_width)

    @staticmethod
    def url_component():
        """
        Return the part of the path that identifies this search type
        """
        return 'sector'

    @staticmethod
    def create(params, save=False):
        """
        Create a sector search centered on the given point
        """
        # calculate the points on the outside of a circle
        # that are sweep_width * 3 from the poi
        # with angles: 30,60,90,120,150,180,210,240,270,300,330,360
        # this order makes the points in clock-order
        query = "SELECT point"
        for deg in (30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 0):
            query += ", ST_Project(point, {sw}, radians({deg})) AS deg_{deg}".format(**{'sw': params.sweep_width() * 3, 'deg': deg})
        query += " FROM data_pointtimelabel WHERE id = {}".format(params.from_geo().pk)
        cursor = dbconn.cursor()
        cursor.execute(query)
        reference_points = cursor.fetchone()

        # Create a SectorSector
        points_order = [0, 12, 2, 8, 10, 4, 6, 0, 1, 3, 9, 11, 5, 7, 0, 2, 4, 10, 12, 6, 8, 0]
        points = []
        for point in points_order:
            points.append(GEOSGeometry(reference_points[point]))

        search = SectorSearch(line=LineString(points), creator=params.creator(), datum=params.from_geo(), created_for=params.asset_type(), sweep_width=params.sweep_width(), mission=params.from_geo().mission)
        if save:
            search.save()

        return search


class ExpandingBoxSearchParams(SearchParams):
    """
    Parameters for an expanding box search
    """
    def __init__(self, from_geo, asset_type, creator, sweep_width, iterations, first_bearing):
        super(ExpandingBoxSearchParams, self).__init__(from_geo, asset_type, creator, sweep_width)
        self._iterations = int(iterations)
        if self._iterations < 1:
            raise ValueError("Iterations must be at least 1")
        self._first_bearing = int(first_bearing)
        if self._first_bearing < 0 or self._first_bearing > 360:
            raise ValueError("First bearing must be between 0 and 360")

    def iterations(self):
        """
        Return the number of complete squares to perform for this search
        """
        return self._iterations

    def first_bearing(self):
        """
        Return the course from the datum to the first point
        """
        return self._first_bearing


class ExpandingBoxSearch(SearchPath):
    """
    An expanding box search from a given point (datum).

    Expanding box searches are good for finding something when you know it was at the datum
    recently (within the last hour)

    A series of straight lines that form a continuous path that expands outwards
    from the datum.
    Each pair of perpendicular lines are n*sweep width (where n is whole number
    that increases every second direction change)
    If the search starts 000 and the sweep width is 100m then it would have lines:
    course (length)
    000 (100m)
    090 (100m)
    180 (200m)
    270 (200m)
    000 (300m)
    090 (300m)
    180 (400m)
    270 (400m)
    And so on, for as many iterations as required (iterations here are groups of 4 lines)

    Expanding boxes have a mathematical property that makes it easy to calculate the
    ends of any line without knowing all the previous ones.
    The first point (b) is 1 sweep width in the starting direction from the datum (a).
    Now all subsequent points expand outwards on a 45 degree angle from either a or b.
    The second, third, forth line all end (start direction +) 45, 135, 225 degrees from
    a, and the fifth line ends (start direction +) 315 degrees, all sqrt(2) * i * sweep
    width (where i is the iteration number) from the reference point (a or b respectively).
    """
    iterations = models.IntegerField()
    first_bearing = models.IntegerField()

    GEOJSON_FIELDS = ('pk', 'created_at', 'created_for', 'inprogress_by', 'sweep_width', 'iterations', 'first_bearing', 'queued_at', 'queued_for_asset', 'queued_for_assettype', )

    def __str__(self):
        return "Expanding Box Search from {} with {} (sw={}, n={}, start={})".format(self.datum, self.created_for, self.sweep_width, self.iterations, self.first_bearing)

    @staticmethod
    def url_component():
        """
        Return the part of the path that identifies this search type
        """
        return 'expandingbox'

    @staticmethod
    def create(params, save=False):
        """
        Create an expanding box search from a given poi
        """
        query = "SELECT p.point, p.first"
        for i in range(1, params.iterations() + 1):
            dist = math.sqrt(2) * i * params.sweep_width()
            query += ", ST_Project(p.point, {}, radians({}))".format(dist, 45 + params.first_bearing())
            query += ", ST_Project(p.point, {}, radians({}))".format(dist, 135 + params.first_bearing())
            query += ", ST_Project(p.point, {}, radians({}))".format(dist, 225 + params.first_bearing())
            query += ", ST_Project(p.first, {}, radians({}))".format(dist, 315 + params.first_bearing())

        query += " FROM (SELECT point, ST_Project(point, {}, radians({})) AS first FROM data_pointtimelabel WHERE id = {}) AS p".format(params.sweep_width(), params.first_bearing(), params.from_geo().pk)

        cursor = dbconn.cursor()
        cursor.execute(query)
        points = [GEOSGeometry(p) for p in cursor.fetchone()]

        search = ExpandingBoxSearch(line=LineString(points), creator=params.creator(), datum=params.from_geo(), created_for=params.asset_type(), sweep_width=params.sweep_width(),
                                    iterations=params.iterations(), first_bearing=params.first_bearing(), mission=params.from_geo().mission)
        if save:
            search.save()

        return search


class TrackLineSearch(SearchPath):
    """
    A track line search following a line.

    Track line searches are useful for checking a path known to be travelled.
    They can also be used as to approximate a feature search (like a shoreline, river, etc).
    No math required, the search has exactly the same points as the reference line.
    """

    GEOJSON_FIELDS = ('pk', 'created_at', 'created_for', 'inprogress_by', 'sweep_width', 'queued_at', 'queued_for_asset', 'queued_for_assettype', )

    def __str__(self):
        return "Track Line Search along {} with {} (sw={})".format(self.datum, self.created_for, self.sweep_width)

    @staticmethod
    def url_component():
        """
        Return the part of the path that identifies this search type
        """
        return 'trackline'

    @staticmethod
    def create(params, save=False):
        """
        Create a track line search that follows a user created line
        """
        search = TrackLineSearch(line=params.from_geo().line, creator=params.creator(), datum=params.from_geo(), created_for=params.asset_type(), sweep_width=params.sweep_width(), mission=params.from_geo().mission)
        if save:
            search.save()
        return search


class TrackLineCreepingSearchParams(SearchParams):
    """
    Parameters for a track line creeping search
    """
    def __init__(self, from_geo, asset_type, creator, sweep_width, width):
        super(TrackLineCreepingSearchParams, self).__init__(from_geo, asset_type, creator, sweep_width)
        self._width = int(width)
        if self._width < 0:
            raise ValueError("Width must be positive")

    def width(self):
        """
        Return the width across the track to search
        (searching will occur width/2 either side of the track)
        """
        return self._width


class TrackLineCreepingSearch(SearchPath):
    """
    A creeping line ahead search following a line.

    A creeping line ahead search (also called a parallel track search) is useful
    for searching a large area methodically.
    This specific implementation centers the search on a line and runs the search
    perpendicular to the line so that runs half the width either side of the line,
    and steps sweep width along the line for each each pass.
    """
    width = models.IntegerField()

    GEOJSON_FIELDS = ('pk', 'created_at', 'created_for', 'inprogress_by', 'sweep_width', 'width', 'queued_at', 'queued_for_asset', 'queued_for_assettype', )

    def __str__(self):
        return "Creeping Search along {} with {} (sw={}, width={})".format(self.datum, self.created_for, self.sweep_width, self.width)

    @staticmethod
    def url_component():
        """
        Return the part of the path that identifies this search type
        """
        return 'creepingline/track'

    @staticmethod
    def create(params, save=False):
        """
        Create a creeping line ahead search from a line
        """
        segment_query = \
            "SELECT ST_PointN(line::geometry, pos)::geography AS start, ST_PointN(line::geometry, pos + 1)::geography AS end" \
            " FROM data_linestringtimelabel, generate_series(1, ST_NPoints(line::geometry) - 1) AS pos WHERE id = {}".format(params.from_geo().pk)

        line_data_query = \
            "SELECT segment.start AS start, ST_Azimuth(segment.start, segment.end) AS direction, ST_Distance(segment.start, segment.end) AS distance FROM ({}) AS segment".format(segment_query)
        line_points_query = \
            "SELECT direction AS direction, ST_Project(linedata.start, {0} * i, direction) AS point"\
            " FROM ({1}) AS linedata, generate_series(0, (linedata.distance/{0})::integer) AS i".format(params.sweep_width(), line_data_query)
        query = \
            "SELECT ST_Project(point, {0}, direction + PI()/2) AS A, ST_Project(point, {0}, direction - PI()/2) AS B FROM ({1}) AS linepoints;".format(params.width(), line_points_query)

        cursor = dbconn.cursor()
        cursor.execute(query)
        db_points = dictfetchall(cursor)

        points = []
        reverse = False
        for segment in db_points:
            if reverse:
                points.append(GEOSGeometry(segment['b']))
                points.append(GEOSGeometry(segment['a']))
                reverse = False
            else:
                points.append(GEOSGeometry(segment['a']))
                points.append(GEOSGeometry(segment['b']))
                reverse = True

        search = TrackLineCreepingSearch(line=LineString(points), creator=params.creator(), datum=params.from_geo(), created_for=params.asset_type(), sweep_width=params.sweep_width(), width=params.width(), mission=params.from_geo().mission)
        if save:
            search.save()

        return search


class PolygonSearch(SearchPath):
    """
    A polygon search for a given area (LinearRing).
    """

    GEOJSON_FIELDS = ('pk', 'created_at', 'created_for', 'inprogress_by', 'sweep_width', 'queued_at', 'queued_for_asset', 'queued_for_assettype', )

    def __str__(self):
        return "Polygon Search inside {} with {} (sw={})".format(
            self.datum,
            self.created_for,
            self.sweep_width)

    @staticmethod
    def url_component():
        """
        Return the part of the path that identifies this search type
        """
        return 'creepingline/polygon'

    @staticmethod
    def create(params, save=False):
        """
        Create a polygon search that sweeps across a polygon
        """
        # See class PolygonTimeLabel in data/models.py
        poly = params.from_geo().polygon
        lrng_lonlat = poly[0]

        skew_point = lrng_lonlat[0]
        lrng_meters = conv_lonlat_to_meters(lrng_lonlat)

        sweep_width = params.sweep_width()

        line_meters = polygon_creep_line(lrng_meters, sweep_width)
        line_lonlat = conv_meters_to_lonlat(line_meters, skew_point)

        search = PolygonSearch(
            line=line_lonlat,
            creator=params.creator(),
            datum=params.from_geo(),
            created_for=params.asset_type(),
            sweep_width=params.sweep_width(),
            mission=params.from_geo().mission)
        if save:
            search.save()
        return search
