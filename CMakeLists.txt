#Copyright (C) 2022 Ghostkeeper
#This plug-in is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
#You should have received a copy of the GNU Affero General Public License along with this plug-in. If not, see <https://gnu.org/licenses/>.

project(SettingsGuide)
cmake_minimum_required(VERSION 3.10.2) #Oldest version it's been tested with.

#Project metadata.
set(SETTINGSGUIDE_PLUGIN_NAME "Settings Guide" CACHE STRING "The name of the plug-in in distribution.")
set(SETTINGSGUIDE_PLUGIN_ID "SettingsGuide2" CACHE STRING "The plug-in ID of the installation in Cura.") #Needs to be '2' because the original plug-in ID was reserved by Asasin for his original version.
set(SETTINGSGUIDE_VERSION_MAJOR 2 CACHE STRING "The major version number, incremented when there is a significant rewrite.")
set(SETTINGSGUIDE_VERSION_MINOR 9 CACHE STRING "The minor version number, incremented when there are new features.")
set(SETTINGSGUIDE_VERSION_PATCH 1 CACHE STRING "The patch version number, incremented if there are only bug fixes and article changes.")
set(SETTINGSGUIDE_SUPPORTED_SDKS "6.0.0;7.0.0;8.0.0" CACHE STRING "List of supported Cura SDK versions.")

#Make sure we have Mistune.
include(ExternalProject)
ExternalProject_Add(Mistune
	GIT_REPOSITORY https://github.com/lepture/mistune.git
	GIT_TAG v0.8.4
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ""
)

#Tests.
option(BUILD_TESTS "Build tests to verify correctness of the plug-in." ON)
if(BUILD_TESTS)
	find_package(Python3 COMPONENTS Interpreter) #Python is required to run the tests.
	enable_testing()
	set(test_packages
		links.py
		markdown_syntax.py
	)
	foreach(test_case ${test_packages})
		add_test(${test_case} ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/test/${test_case}")
	endforeach()
endif()

#Installation.
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/plugin.json.in" plugin.json)
set(installed_files
	__init__.py
	CuraSettingsGuide.py
	LICENSE.md
	MenuItemHandler.py
	QtMarkdownRenderer.py
	README.md
)
set(installed_files_resources_icons
	arrow.svg
	camera.svg
	icon.svg
	play.svg
	translations.svg
)
set(installed_files_resources
	settings_guide_definitions.def.json
)
set(installed_files_resources_qml
	ArticleCheckbox.qml
	ArticleImages.qml
	ArticleText.qml
	SettingsGuide.qml
	SettingsSidebar.qml
	TranslationButton.qml
)
set(installed_files_resources_qml_SidebarSettings
	SettingCategory.qml
	SettingCheckBox.qml
	SettingComboBox.qml
	SettingItem.qml
	SettingTextField.qml
)
set(installed_files_resources_qml_cura4
	ArticleCheckbox.qml
	ArticleImages.qml
	ArticleText.qml
	SettingsGuide.qml
	SettingsSidebar.qml
	TranslationButton.qml
)
set(installed_files_resources_qml_cura4_SidebarSettings
	SettingCategory.qml
	SettingCheckBox.qml
	SettingComboBox.qml
	SettingExtruder.qml
	SettingItem.qml
	SettingTextField.qml
)
set(installed_paths "")
foreach(f IN LISTS installed_files)
	list(APPEND installed_paths ${CMAKE_CURRENT_SOURCE_DIR}/${f})
endforeach()
list(APPEND installed_paths ${CMAKE_CURRENT_BINARY_DIR}/plugin.json)
set(installed_paths_resources "")
foreach(f IN LISTS installed_files_resources)
	list(APPEND installed_paths_resources ${CMAKE_CURRENT_SOURCE_DIR}/resources/${f})
endforeach()
set(installed_paths_resources_icons "")
foreach(f IN LISTS installed_files_resources_icons)
	list(APPEND installed_paths_resources_icons ${CMAKE_CURRENT_SOURCE_DIR}/resources/icons/${f})
endforeach()
set(installed_paths_resources_qml "")
foreach(f IN LISTS installed_files_resources_qml)
	list(APPEND installed_paths_resources_qml ${CMAKE_CURRENT_SOURCE_DIR}/resources/qml/${f})
endforeach()
set(installed_paths_resources_qml_SidebarSettings "")
foreach(f IN LISTS installed_files_resources_qml_SidebarSettings)
	list(APPEND installed_paths_resources_qml_SidebarSettings ${CMAKE_CURRENT_SOURCE_DIR}/resources/qml/SidebarSettings/${f})
endforeach()
set(installed_paths_resources_qml_cura4 "")
foreach(f IN LISTS installed_files_resources_qml_cura4)
	list(APPEND installed_paths_resources_qml_cura4 ${CMAKE_CURRENT_SOURCE_DIR}/resources/qml_cura4/${f})
endforeach()
set(installed_paths_resources_qml_cura4_SidebarSettings "")
foreach(f IN LISTS installed_files_resources_qml_cura4_SidebarSettings)
	list(APPEND installed_paths_resources_qml_cura4_SidebarSettings ${CMAKE_CURRENT_SOURCE_DIR}/resources/qml_cura4/SidebarSettings/${f})
endforeach()

#Find out where to install this thing.
if(WIN32)
	set(cura_directory "$ENV{APPDATA}\\cura")
elseif(APPLE)
	set(cura_directory "$ENV{HOME}/Library/Application Support/cura")
else()
	set(cura_directory "$ENV{HOME}/.local/share/cura")
endif()
#Figure out the latest Cura release that's installed.
file(GLOB versions RELATIVE "${cura_directory}" "${cura_directory}/*")
set(latest_version 2.0)
foreach(version ${versions})
	if(IS_DIRECTORY "${cura_directory}/${version}")
		if(${version} VERSION_GREATER ${latest_version})
			set(latest_version ${version})
		endif()
	endif()
endforeach()
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
	set(CMAKE_INSTALL_PREFIX "${cura_directory}/${latest_version}/plugins" CACHE PATH "Location of the Cura plug-ins folder to install this plug-in to." FORCE)
endif()
install(FILES ${installed_paths} DESTINATION ${SETTINGSGUIDE_PLUGIN_ID})
install(FILES ${installed_paths_resources} DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/resources)
install(FILES ${installed_paths_resources_icons} DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/resources/icons)
install(FILES ${installed_paths_resources_qml} DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/resources/qml)
install(FILES ${installed_paths_resources_qml_SidebarSettings} DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/resources/qml/SidebarSettings)
install(FILES ${installed_paths_resources_qml_cura4} DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/resources/qml_cura4)
install(FILES ${installed_paths_resources_qml_cura4_SidebarSettings} DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/resources/qml_cura4/SidebarSettings)
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/resources/articles" DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/resources)
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/resources/translations" DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/resources)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/Mistune-prefix/src/Mistune/mistune.py" DESTINATION ${SETTINGSGUIDE_PLUGIN_ID}/Mistune)

#Packing this into a .curapackage file.
add_custom_target(pack COMMAND "") #Packs for all supported SDK versions.
set(packaged_files
	package.json
	[Content_Types].xml
	_rels
	files
)
foreach(sdk_version ${SETTINGSGUIDE_SUPPORTED_SDKS})
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/cmake/package.json.in" pack${sdk_version}/package.json)
	add_custom_target(pack${sdk_version}
		COMMAND ${CMAKE_COMMAND} -E make_directory files/plugins/${SETTINGSGUIDE_PLUGIN_ID}
		COMMAND ${CMAKE_COMMAND} -E copy_if_different ${installed_paths} files/plugins/${SETTINGSGUIDE_PLUGIN_ID}
		COMMAND ${CMAKE_COMMAND} -E make_directory files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources
		COMMAND ${CMAKE_COMMAND} -E copy_if_different ${installed_paths_resources} files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources
		COMMAND ${CMAKE_COMMAND} -E make_directory files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/icons
		COMMAND ${CMAKE_COMMAND} -E copy_if_different ${installed_paths_resources_icons} files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/icons
		COMMAND ${CMAKE_COMMAND} -E make_directory files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/qml
		COMMAND ${CMAKE_COMMAND} -E copy_if_different ${installed_paths_resources_qml} files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/qml
		COMMAND ${CMAKE_COMMAND} -E make_directory files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/qml/SidebarSettings
		COMMAND ${CMAKE_COMMAND} -E copy_if_different ${installed_paths_resources_qml_SidebarSettings} files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/qml/SidebarSettings
		COMMAND ${CMAKE_COMMAND} -E make_directory files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/qml_cura4
		COMMAND ${CMAKE_COMMAND} -E copy_if_different ${installed_paths_resources_qml_cura4} files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/qml_cura4
		COMMAND ${CMAKE_COMMAND} -E make_directory files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/qml_cura4/SidebarSettings
		COMMAND ${CMAKE_COMMAND} -E copy_if_different ${installed_paths_resources_qml_cura4_SidebarSettings} files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/qml_cura4/SidebarSettings
		COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/resources/articles" files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/articles
		COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/resources/translations" files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/resources/translations
		COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/cmake/[Content_Types].xml" .
		COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/cmake/_rels" _rels
		COMMAND ${CMAKE_COMMAND} -E make_directory files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/Mistune
		COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_BINARY_DIR}/Mistune-prefix/src/Mistune/mistune.py" files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/Mistune
		COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_BINARY_DIR}/Mistune-prefix/src/Mistune/LICENSE" files/plugins/${SETTINGSGUIDE_PLUGIN_ID}/Mistune
		COMMAND ${CMAKE_COMMAND} -E tar cfv ../SettingsGuide${SETTINGSGUIDE_VERSION_MAJOR}.${SETTINGSGUIDE_VERSION_MINOR}.${SETTINGSGUIDE_VERSION_PATCH}-sdk${sdk_version}.curapackage --format=zip ${packaged_files}
		WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/pack${sdk_version}
		DEPENDS Mistune
	)
	add_dependencies(pack pack${sdk_version})
endforeach()

#Let CPack find it.
include(InstallRequiredSystemLibraries)
set(CPACK_PACKAGE_VERSION_MAJOR ${SETTINGSGUIDE_VERSION_MAJOR})
set(CPACK_PACKAGE_VERSION_MINOR ${SETTINGSGUIDE_VERSION_MINOR})
set(CPACK_PACKAGE_VERSION_PATCH ${SETTINGSGUIDE_VERSION_PATCH})
set(CPACK_PACKAGE_NAME ${SETTINGSGUIDE_PLUGIN_NAME})
set(CPACK_PACKAGE_DESCRIPTION_FILE ${CMAKE_CURRENT_SOURCE_DIR}/README.md)
set(CPACK_GENERATOR ZIP)
include(CPack)
