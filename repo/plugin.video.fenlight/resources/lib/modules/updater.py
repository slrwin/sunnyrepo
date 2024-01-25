# -*- coding: utf-8 -*-
import shutil
import time
import sqlite3 as database
from zipfile import ZipFile
from modules.utils import string_alphanum_to_num
from modules.settings import update_use_test_repo
from modules import kodi_utils 
# logger = kodi_utils.logger

update_kodi_addons_db, notification, show_text, confirm_dialog = kodi_utils.update_kodi_addons_db, kodi_utils.notification, kodi_utils.show_text, kodi_utils.confirm_dialog
requests, addon_info, unzip, confirm_dialog, ok_dialog = kodi_utils.requests, kodi_utils.addon_info, kodi_utils.unzip, kodi_utils.confirm_dialog, kodi_utils.ok_dialog
update_local_addons, disable_enable_addon, close_all_dialog = kodi_utils.update_local_addons, kodi_utils.disable_enable_addon, kodi_utils.close_all_dialog
translate_path, osPath, delete_file, execute_builtin = kodi_utils.translate_path, kodi_utils.osPath, kodi_utils.delete_file, kodi_utils.execute_builtin

packages_dir = translate_path('special://home/addons/packages/')
home_addons_dir = translate_path('special://home/addons/')
destination_check = translate_path('special://home/addons/plugin.video.fenlight/')
changelog_location = translate_path('special://home/addons/plugin.video.fenlight/resources/text/changelog.txt')
addon_dir = 'plugin.video.fenlight'
repo_location = {True: 'tikipeter.test', False: 'tikipeter.github.io'}
zipfile_name = 'plugin.video.fenlight-%s.zip'
versions_url = 'https://github.com/Tikipeter/%s/raw/main/packages/fen_light_version'
location_url = 'https://github.com/Tikipeter/%s/raw/main/packages/%s'
heading_str = 'Fen Light Updater'
notification_error_str = 'Fen Light Update Error'
notification_occuring_str = 'Fen Light Update Occuring'
notification_available_str = 'Fen Light Update Available'
notification_updating_str = 'Fen Light Performing Update'
result_line = 'Installed Version: [B]%s[/B][CR]Online%s Version: [B]%s[/B][CR][CR] %s'
no_update_line = '[B]No Update Available[/B]'
update_available_line = '[B]An Update is Available[/B][CR]Perform Update?'
success_line = '[CR]Success.[CR]Fen Light updated to version [B]%s[/B]'
error_line = 'Error Updating.[CR]Please install new update manually'


def get_versions(use_test_repo):
	try:
		result = requests.get(versions_url % repo_location[use_test_repo])
		if result.status_code != 200: return None, None
		online_version = result.text.replace('\n', '')
		current_version = addon_info('version')
		return current_version, online_version
	except: return None, None

def perform_update(current_version, online_version, use_test_repo):
	if use_test_repo: return current_version != online_version
	else: return string_alphanum_to_num(current_version) != string_alphanum_to_num(online_version)

def update_check(action=4):
	use_test_repo = update_use_test_repo()
	if action == 3: return
	online_type = ' [B]Test[/B]' if use_test_repo else ''
	current_version, online_version = get_versions(use_test_repo)
	if not current_version: return notification(notification_error_str)
	if not perform_update(current_version, online_version, use_test_repo):
		if action == 4: return ok_dialog(heading=heading_str, text=result_line % (current_version, online_type, online_version, no_update_line))
		return
	if action in (0, 4):
		if not confirm_dialog(heading=heading_str, text=result_line % (current_version, online_type, online_version, update_available_line)): return
	if action == 1: notification(notification_occuring_str)
	if action == 2: return notification(notification_available_str)
	return update_addon(online_version, action, use_test_repo)

def update_addon(new_version, action, use_test_repo):
	close_all_dialog()
	execute_builtin('ActivateWindow(Home)', True)
	notification(notification_updating_str)
	zip_name = zipfile_name % new_version
	url = location_url % (repo_location[use_test_repo], zip_name)
	result = requests.get(url, stream=True)
	if result.status_code != 200: return ok_dialog(heading=heading_str, text=error_line)
	zip_location = osPath.join(packages_dir, zip_name)
	with open(zip_location, 'wb') as f: shutil.copyfileobj(result.raw, f)
	shutil.rmtree(osPath.join(home_addons_dir, addon_dir))
	success = unzip(zip_location, home_addons_dir, destination_check)
	delete_file(zip_location)
	if not success: return ok_dialog(heading=heading_str, text=error_line)
	if action in (0, 4) and confirm_dialog(heading=heading_str, text=success_line % new_version, ok_label='Changelog', cancel_label='Exit', default_control=10) != False:
			show_text('Changelog', file=changelog_location, font_size='large')
	update_local_addons()
	disable_enable_addon()
	update_kodi_addons_db()
