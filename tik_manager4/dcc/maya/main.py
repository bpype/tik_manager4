"""Main module for Maya DCC integration."""

from pathlib import Path
import logging
import platform

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import cmds
from maya import mel
import maya.OpenMaya as om
from maya import OpenMayaUI as omui

from tik_manager4.ui.Qt import QtWidgets, QtCompat
from tik_manager4.ui.main import MainUI as tik4_main
from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.maya import utils
from tik_manager4.dcc.maya import panels
from tik_manager4.dcc.maya import validate
from tik_manager4.dcc.maya import extract
from tik_manager4.dcc.maya import ingest
from tik_manager4.dcc.maya import extension

LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    """Maya DCC class."""

    name = "Maya"
    formats = [".ma", ".mb"]
    preview_enabled = True  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes
    extensions = extension.classes
    custom_launcher = True
    save_selection_enabled = True

    @staticmethod
    def get_main_window():
        """Get the memory adress of the main window to connect Qt dialog to it.
        Returns:
            (long or int) Memory Adress
        """
        try:
            win = omui.MQtUtil_mainWindow()
        except AttributeError:  # Maya 2025 / Qt 6
            win = omui.MQtUtil.mainWindow()
        ptr = QtCompat.wrapInstance(int(win), QtWidgets.QMainWindow)
        return ptr

    @staticmethod
    def save_scene():
        """Saves the current file"""
        cmds.file(save=True)

    @staticmethod
    def save_as(file_path):
        """Save the current scene as a new file.
        Args:
            file_path (str): The file path to save the scene to.
        Returns:
            (str) The file path that the scene was saved to.
        """
        extension = Path(file_path).suffix
        file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        cmds.file(rename=file_path)
        cmds.file(save=True, type=file_format)
        return file_path

    @staticmethod
    def save_selection(file_path):
        """Save the current selection as a new file."""
        extension = Path(file_path).suffix
        file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        cmds.file(file_path, force=True, options="v=0;", type=file_format, exportSelected=True)
        return file_path

    @staticmethod
    def save_prompt():
        """Pop up the save prompt."""
        cmds.SaveScene()
        return True  # this is important or else will be an indefinite loop

    @staticmethod
    def open(file_path, force=True, **_extra_arguments):
        """Open the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **_extra_arguments: Compatibility arguments for other DCCs

        Returns: None
        """
        cmds.file(file_path, open=True, force=force)

    @staticmethod
    def get_ranges():
        """Get the viewport ranges."""
        return utils.get_ranges()

    @staticmethod
    def set_ranges(range_list):
        """Set the timeline ranges."""
        utils.set_ranges(range_list)

    @staticmethod
    def set_project(file_path):
        """
        Sets the project to the given path
        Args:
            file_path: (String) Path to the project folder

        Returns: None

        """
        cmds.workspace(file_path, openWorkspace=True)

    @staticmethod
    def is_modified():
        """Returns True if the scene has unsaved changes"""
        # an empty string (not saved) should return False IF the scene is empty
        # not having any DAG objects in the scene doesnt necessarily mean the scene is empty
        # but we will assume that for now.
        default_dag_nodes = [
            "persp",
            "perspShape",
            "top",
            "topShape",
            "front",
            "frontShape",
            "side",
            "sideShape",
        ]
        if cmds.ls(dag=True) == default_dag_nodes:
            return False
        return cmds.file(query=True, modified=True)

    @staticmethod
    def get_scene_file():
        """Get the current scene file."""
        # This logic is borrowed from the pymel implementation of sceneName().

        # Get the name for untitled files in Maya.
        untitled_file_name = mel.eval("untitledFileName()")
        path = om.MFileIO.currentFile()

        file_name = Path(path).name
        # Don't just use cmds.file(q=1, sceneName=1)
        # because it was sometimes returning an empty string,
        # even when there was a valid file
        # Check both the OpenMaya.MFileIO.currentFile() and
        # the cmds.file(q=1, sceneName=1)
        # so as to be sure that no file is open.
        # This should mean that if someone does have
        # a file open and it's named after the untitledFileName we should still
        # be able to return the path.
        if (
            file_name.startswith(untitled_file_name)
            and cmds.file(q=1, sceneName=1) == ""
        ):
            return ""
        return path

    @staticmethod
    def get_current_frame():
        """Return current frame in timeline.
        If dcc does not have a timeline, returns None.
        """
        return cmds.currentTime(query=True)

    def generate_thumbnail(self, file_path, width, height):
        """
        Grabs a thumbnail from the current scene
        Args:
            file_path: (String) File path to save the thumbnail
            width: (Int) Width of the thumbnail
            height: (Int) Height of the thumbnail

        Returns: None

        """

        # create a thumbnail using playblast
        frame = self.get_current_frame()
        store = cmds.getAttr("defaultRenderGlobals.imageFormat")
        cmds.setAttr(
            "defaultRenderGlobals.imageFormat", 8
        )  # This is the value for jpeg
        cmds.playblast(
            completeFilename=file_path,
            forceOverwrite=True,
            format="image",
            width=width,
            height=height,
            showOrnaments=False,
            frame=[frame],
            viewer=False,
            percent=100,
        )
        cmds.setAttr("defaultRenderGlobals.imageFormat", store)  # take it back
        return file_path

    @staticmethod
    def get_scene_fps():
        """Return the current FPS value set by DCC. None if not supported."""
        return utils.get_scene_fps()

    @staticmethod
    def set_scene_fps(fps_value):
        """
        Set the FPS value in DCC if supported.
        Args:
            fps_value: (integer) fps value

        Returns: None

        """
        utils.set_scene_fps(fps_value)

    @staticmethod
    def get_scene_cameras():
        """
        Return a dictionary of all the cameras in the scene where key is the camera name and value is the camera uuid.
        """
        all_cameras = cmds.ls(type="camera")
        _dict = {}
        for cam in all_cameras:
            _dict[cmds.listRelatives(cam, parent=True)[0]] = cmds.ls(cam, uuid=True)[0]
        return _dict

    @staticmethod
    def get_current_camera():
        """Get the current camera and its uuid."""
        camera = cmds.modelPanel(cmds.getPanel(withFocus=True), query=True, camera=True)
        return camera, cmds.ls(camera, uuid=True)[0]

    @staticmethod
    def _get_formats_and_codecs():
        """Return the codecs which can be used in current workstation"""
        format_list = cmds.playblast(query=True, format=True)
        codecs_dict = dict(
            (item, mel.eval('playblast -format "{0}" -q -compression;'.format(item)))
            for item in format_list
        )
        return codecs_dict

    @staticmethod
    def _get_format_and_codec():
        """Return the best format and codec for the current workstation"""
        available_codecs = Dcc._get_formats_and_codecs()
        favored_formats = ["qt", "avi"]
        favored_codecs = ["H.264", "jpg", "MPEG-4 Video", "none"]
        for format_ in favored_formats:
            for codec in favored_codecs:
                if codec in available_codecs.get(format_, []):
                    favored_extension = "mov" if format_ == "qt" else "avi"
                    return format_, codec, favored_extension
        return None, None, None

    @staticmethod
    def generate_preview(name, folder, camera_code, resolution, range, settings=None):
        """
        Create a preview from the current scene
        Args:
            name: (String) Name of the preview
            folder: (String) Folder to save the preview
            camera_code: (String) Camera code. In Maya, this is the UUID of the camera transform node.
            resolution: (list) Resolution of the preview
            range: (list) Range of the preview
            settings: (dict) Global Settings dictionary
        """

        settings = settings or {
            "DisplayFieldChart": False,
            "DisplayGateMask": False,
            "DisplayFilmGate": False,
            "DisplayFilmOrigin": False,
            "DisplayFilmPivot": False,
            "DisplayResolution": False,
            "DisplaySafeAction": False,
            "DisplaySafeTitle": False,
            "DisplayAppearance": "smoothShaded",
            "ClearSelection": True,
            "ShowFrameNumber": True,
            "ShowFrameRange": True,
            "CrfValue": 23,
            "Format": "video",
            "PostConversion": True,
            "ShowFPS": True,
            "PolygonOnly": True,
            "Percent": 100,
            "DisplayTextures": True,
            "ShowGrid": False,
            "ShowSceneName": False,
            "UseDefaultMaterial": False,
            "ViewportAsItIs": False,
            "HudsAsItIs": False,
            "WireOnShaded": False,
            "Codec": "png",
            "ShowCategory": False,
            "Quality": 100,
        }

        playback_slider = mel.eval("$tmpVar=$gPlayBackSlider")
        active_sound = cmds.timeControl(playback_slider, q=True, sound=True)

        # get the best codec for the format
        output_format, output_codec, extension = Dcc._get_format_and_codec()

        if not output_format or not output_codec:
            LOG.error("No suitable codec found for the current workstation")
            return None

        # Create pb panel and adjust it due to settings
        _camera = cmds.ls(camera_code)[0]
        # we need to make sure that we are getting the transform of the camera
        # not the shape node. This is for a workaround for the panel manager.
        if cmds.objectType(_camera) == "camera":
            _camera = cmds.listRelatives(_camera, parent=True, type="transform")[0]

        pb_panel = panels.PanelManager(_camera, resolution, inherit=True)

        if not settings.get("ViewportAsItIs"):
            pb_panel.display_field_chart = settings.get("DisplayFieldChart", False)
            pb_panel.display_gate_mask = settings.get("DisplayGateMask", False)
            pb_panel.display_film_gate = settings.get("DisplayFilmGate", False)
            pb_panel.display_film_origin = settings.get("DisplayFilmOrigin", False)
            pb_panel.display_film_pivot = settings.get("DisplayFilmPivot", False)
            pb_panel.display_resolution = settings.get("DisplayResolution", False)
            pb_panel.display_safe_action = settings.get("DisplaySafeAction", False)
            pb_panel.display_safe_title = settings.get("DisplaySafeTitle", False)

            pb_panel.all_objects = not settings.get("PolygonOnly", True)
            pb_panel.display_appearance = settings.get(
                "DisplayAppearance", "smoothShaded"
            )
            pb_panel.display_textures = settings.get("DisplayTextures", True)
            pb_panel.grid = settings.get("ShowGrid", False)
            pb_panel.use_default_material = settings.get("UseDefaultMaterial", False)
            pb_panel.polymeshes = True
            pb_panel.image_plane = True

        if not settings.get("HudsAsItIs"):
            pb_panel.hud = False

        _output = cmds.playblast(
            format=output_format,
            # sequenceTime=sequenceTime,
            filename=str(Path(folder) / name),
            widthHeight=resolution,
            percent=settings.get("Percent", 100),
            quality=settings.get("Quality", 100),
            compression=output_codec,
            sound=active_sound,
            # useTraxSounds=True,
            viewer=False,
            offScreen=True,
            offScreenViewportUpdate=True,
            activeEditor=False,
            editorPanelName=pb_panel.panel,
            startTime=range[0],
            endTime=range[1],
        )
        if not _output:
            LOG.error("Playblast failed")
            pb_panel.kill()
            return None

        final_clip = f"{_output}.{extension}"
        pb_panel.kill()
        return final_clip

    @staticmethod
    def get_dcc_version():
        """Return the DCC major version."""
        return str(cmds.about(query=True, majorVersion=True))

    def launch(self, tik_main_object, window_name=None, dont_show=False):
        """Launch Tik Main UI with DCC specific way."""
        parent = self.get_main_window()



        workspace_name = f"{window_name}WorkspaceControl"
        if cmds.workspaceControl(workspace_name, query=True, exists=True):
            cmds.workspaceControl(workspace_name, edit=True, close=True)
            cmds.deleteUI(workspace_name, control=True)

        if not dont_show:
            main_ui = DockableMainUI(main_object=tik_main_object, window_name=window_name, parent=parent)
            main_ui.show(dockable=True)
        else:
            all_widgets = QtWidgets.QApplication.allWidgets()
            for entry in all_widgets:
                try:
                    if entry.objectName() == window_name+"NoShow":
                        # if entry.objectName().startswith("Tik Manager"):
                        entry.close()
                        entry.deleteLater()
                except (AttributeError, TypeError):
                    pass
            main_ui = RegularMainUI(main_object=tik_main_object, parent=parent, window_name=window_name+"NoShow")

        return main_ui


class RegularMainUI(tik4_main):
    def __init__(self, main_object=None, window_name=None, parent=None, **kwargs):
        super(RegularMainUI, self).__init__(main_object=main_object, window_name=window_name, parent=parent, **kwargs)
        # make sure it is getting created center according to the parent
        self.move(parent.frameGeometry().center() - self.rect().center())

class DockableMainUI(MayaQWidgetDockableMixin, tik4_main):
    def __init__(self, main_object=None, window_name=None, parent=None, **kwargs):
        super(DockableMainUI, self).__init__(main_object=main_object, window_name=window_name, parent=parent, **kwargs)

    def dockCloseEventTriggered(self):  # pylint: disable=invalid-name
        """Override the stub function to save the window state."""
        self.tik.user.last_subproject = None
        self.tik.user.last_task = None
        self.tik.user.last_category = None
        self.tik.user.last_work = None
        self.tik.user.last_version = None

        self.set_last_state()

        # set the expanded state of the subproject tree
        self.tik.user.expanded_subprojects = (
            self.subprojects_mcv.sub_view.get_expanded_state()
        )

        self.tik.user.resume.apply_settings()
        _ = QtWidgets.QApplication.allWidgets()
