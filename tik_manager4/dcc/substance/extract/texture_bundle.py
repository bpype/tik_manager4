"""Extract the textures."""

import math

from pathlib import Path

import substance_painter

from tik_manager4.dcc.extract_core import ExtractCore

class Textures(ExtractCore):
    """Extract Textures."""

    nice_name = "Texture Bundle"
    color = (50, 150, 50)
    bundled = True

    # def __init__(self):
    #     super(Textures, self).__init__()
    #
    #     self.extension = ".spp"


    def _extract_default(self):
        """Extract the textures."""
        if not substance_painter.project.is_open():
            raise ValueError("No project is open.")

        _str_directory = self.resolve_output()
        bundle_directory = Path(_str_directory)
        bundle_directory.mkdir(parents=True, exist_ok=True)

        export_preset = substance_painter.resource.ResourceID(
            context="starter_assets", name="PBR Metallic Roughness")

        # List all the Texture Sets:
        for texture_set in substance_painter.textureset.all_texture_sets():
            for stack in texture_set.all_stacks():
                # Get stack name
                stack_name = str(stack)

                # Get stack resolution (in powers of 2)
                material = stack.material()
                resolution = material.get_resolution()
                sizeLog2 = int(math.log2(resolution.width))

                # Export
                export_list = [{"rootPath": stack_name}]

                # You can also use a suffix to only export variations on a basecolor map
                self.__export(bundle_directory.as_posix(), export_list, export_preset)

    def __export(self, folder_path, export_list, export_preset):
        export_config = {
                "exportShaderParams" : False,
                "exportPath" 			: folder_path,
                "exportList"			: export_list,
                "defaultExportPreset" 	: export_preset.url(),
                "exportParameters" 		: [
                    {
                        "parameters"	: { "paddingAlgorithm": "infinite", "sizeLog2" :  12, "fileFormat" : "exr" },
                    }
                ]
            }

        substance_painter.export.export_project_textures(export_config)
        return
