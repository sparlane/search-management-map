# Generated by Django 3.0.6 on 2020-05-23 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0015_auto_20200523_1706'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='expandingboxsearch',
            name='search_expa_created_e5c35d_idx',
        ),
        migrations.RemoveIndex(
            model_name='expandingboxsearch',
            name='search_expa_inprogr_8a4fb0_idx',
        ),
        migrations.RemoveIndex(
            model_name='expandingboxsearch',
            name='search_expa_complet_375b1c_idx',
        ),
        migrations.RemoveIndex(
            model_name='expandingboxsearch',
            name='search_expa_mission_bcdb9f_idx',
        ),
        migrations.RemoveIndex(
            model_name='expandingboxsearch',
            name='search_expa_deleted_e33db8_idx',
        ),
        migrations.RemoveIndex(
            model_name='polygonsearch',
            name='search_poly_created_ae79e2_idx',
        ),
        migrations.RemoveIndex(
            model_name='polygonsearch',
            name='search_poly_inprogr_f9d901_idx',
        ),
        migrations.RemoveIndex(
            model_name='polygonsearch',
            name='search_poly_complet_28b10e_idx',
        ),
        migrations.RemoveIndex(
            model_name='polygonsearch',
            name='search_poly_mission_7e0746_idx',
        ),
        migrations.RemoveIndex(
            model_name='polygonsearch',
            name='search_poly_deleted_bc718a_idx',
        ),
        migrations.RemoveIndex(
            model_name='sectorsearch',
            name='search_sect_created_03cdb4_idx',
        ),
        migrations.RemoveIndex(
            model_name='sectorsearch',
            name='search_sect_inprogr_64e49d_idx',
        ),
        migrations.RemoveIndex(
            model_name='sectorsearch',
            name='search_sect_complet_66b82f_idx',
        ),
        migrations.RemoveIndex(
            model_name='sectorsearch',
            name='search_sect_mission_76d1f4_idx',
        ),
        migrations.RemoveIndex(
            model_name='sectorsearch',
            name='search_sect_deleted_e68757_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinecreepingsearch',
            name='search_trac_created_f6c6fc_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinecreepingsearch',
            name='search_trac_inprogr_68a38f_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinecreepingsearch',
            name='search_trac_complet_548169_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinecreepingsearch',
            name='search_trac_mission_92ab25_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinecreepingsearch',
            name='search_trac_deleted_a66ae2_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinesearch',
            name='search_trac_created_d09889_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinesearch',
            name='search_trac_inprogr_5e4765_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinesearch',
            name='search_trac_complet_8c7680_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinesearch',
            name='search_trac_mission_0d86e7_idx',
        ),
        migrations.RemoveIndex(
            model_name='tracklinesearch',
            name='search_trac_deleted_205a8e_idx',
        ),
        migrations.RenameField(
            model_name='expandingboxsearch',
            old_name='completed',
            new_name='completed_at',
        ),
        migrations.RenameField(
            model_name='polygonsearch',
            old_name='completed',
            new_name='completed_at',
        ),
        migrations.RenameField(
            model_name='sectorsearch',
            old_name='completed',
            new_name='completed_at',
        ),
        migrations.RenameField(
            model_name='tracklinecreepingsearch',
            old_name='completed',
            new_name='completed_at',
        ),
        migrations.RenameField(
            model_name='tracklinesearch',
            old_name='completed',
            new_name='completed_at',
        ),
        migrations.AddIndex(
            model_name='expandingboxsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'created_at', 'completed_at'], name='search_expa_mission_0aabbc_idx'),
        ),
        migrations.AddIndex(
            model_name='expandingboxsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at'], name='search_expa_mission_cd781d_idx'),
        ),
        migrations.AddIndex(
            model_name='expandingboxsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by'], name='search_expa_mission_57e17e_idx'),
        ),
        migrations.AddIndex(
            model_name='expandingboxsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'created_for'], name='search_expa_mission_56eaac_idx'),
        ),
        migrations.AddIndex(
            model_name='expandingboxsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'queued_for_asset', 'queued_for_assettype'], name='search_expa_mission_12aa16_idx'),
        ),
        migrations.AddIndex(
            model_name='polygonsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'created_at', 'completed_at'], name='search_poly_mission_c29d24_idx'),
        ),
        migrations.AddIndex(
            model_name='polygonsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at'], name='search_poly_mission_2575ff_idx'),
        ),
        migrations.AddIndex(
            model_name='polygonsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by'], name='search_poly_mission_a69c09_idx'),
        ),
        migrations.AddIndex(
            model_name='polygonsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'created_for'], name='search_poly_mission_10991d_idx'),
        ),
        migrations.AddIndex(
            model_name='polygonsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'queued_for_asset', 'queued_for_assettype'], name='search_poly_mission_ad06fb_idx'),
        ),
        migrations.AddIndex(
            model_name='sectorsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'created_at', 'completed_at'], name='search_sect_mission_8172e1_idx'),
        ),
        migrations.AddIndex(
            model_name='sectorsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at'], name='search_sect_mission_9b633b_idx'),
        ),
        migrations.AddIndex(
            model_name='sectorsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by'], name='search_sect_mission_258568_idx'),
        ),
        migrations.AddIndex(
            model_name='sectorsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'created_for'], name='search_sect_mission_0a6735_idx'),
        ),
        migrations.AddIndex(
            model_name='sectorsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'queued_for_asset', 'queued_for_assettype'], name='search_sect_mission_9d1085_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinecreepingsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'created_at', 'completed_at'], name='search_trac_mission_f259c5_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinecreepingsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at'], name='search_trac_mission_7a3b47_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinecreepingsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by'], name='search_trac_mission_d8f08d_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinecreepingsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'created_for'], name='search_trac_mission_9d0cd5_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinecreepingsearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'queued_for_asset', 'queued_for_assettype'], name='search_trac_mission_d05649_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinesearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'created_at', 'completed_at'], name='search_trac_mission_84d3c4_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinesearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at'], name='search_trac_mission_9e7a2c_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinesearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by'], name='search_trac_mission_a92aad_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinesearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'created_for'], name='search_trac_mission_ad59f2_idx'),
        ),
        migrations.AddIndex(
            model_name='tracklinesearch',
            index=models.Index(fields=['mission', 'deleted_at', 'replaced_at', 'completed_at', 'inprogress_by', 'queued_for_asset', 'queued_for_assettype'], name='search_trac_mission_aa5e01_idx'),
        ),
    ]