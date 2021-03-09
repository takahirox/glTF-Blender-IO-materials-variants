# glTF-Blender-IO-materials-variants

**glTF-Blender-IO-materials-variants** is a [Blender](https://www.blender.org/) addon for [glTF `KHR_materials_variants` extension](https://github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_materials_variants) on top of [`KHR_Blender-IO`](https://github.com/KhronosGroup/glTF-Blender-IO) addon.

## Compatible Blender version

&gt;= 2.91

## How to install

### Ensure the `glTF-Blender-IO` addon is installed and enabled

Ensure the `glTF-Blender-IO` addon is installed and enabled in your Blender because the `glTF-Blender-IO-materials_variants` addon works on top of it.  You can check it by Edit -> Preferences -> Add-ons -> "glTF 2.0" in the search bar. The `glTF-Blender-IO` addon should be listed as `Import-Export: glTF 2.0 format`. It should be installed and enabled by default.

![Ensure glTF-Blender-IO is installed and enabled](https://user-images.githubusercontent.com/7637832/110406787-a41f3f80-8037-11eb-9e12-163aafd5f08e.png)
 
### Download the zip archived source code

Download the zip archived source code from the [Releases](https://github.com/takahirox/glTF-Blender-IO-materials-variants/releases).

![Download the zip archived source code from the Releases](https://user-images.githubusercontent.com/7637832/110403357-d29a1c00-8031-11eb-993f-d977fb3c681f.png)

### Install `glTF-Blender-IO-materials-variants` addon

Install the `glTF-Blender-IO-materials-variants` addon to your Blender via Edit -> Preferences -> Add-ons -> Install -> Select the downloaded file

![Edit -> Preferences](https://user-images.githubusercontent.com/7637832/110405180-062a7580-8035-11eb-839a-f5008a992f92.png)

![Add-ons -> Install](https://user-images.githubusercontent.com/7637832/110405413-70dbb100-8035-11eb-9860-3f4867427246.png)

![Select the downloaded file](https://user-images.githubusercontent.com/7637832/110405696-d039c100-8035-11eb-9aff-71ba105187c3.png)

### Ensure the addon is installed and enabled.

Ensure the addon is installed and enabled. You can easily find the addon by inputting "KHR_materials_variants" in the search bar.

![Ensure the addon is enabled](https://user-images.githubusercontent.com/7637832/110406566-4db20100-8037-11eb-9cf2-4a73fcf676bd.png)

## Features

The addon enables to import, export, and edit support the [glTF `KHR_materials_variants` extension](https://github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_materials_variants) in Blender.

## How to use

The addon adds the "Materials Variants" panel to the Object property. You can add, remove, and edit the variants (alternate) materials for an mesh object in the panel. And the addon imports the `KHR_materials_variants` extension to the panel.

![Materials Variants panel](https://user-images.githubusercontent.com/7637832/110414708-3f6ae180-8045-11eb-86f6-cbf5a2848388.png)

The addon also imports the `KHR_materials_variants` extension materials into the material slots of a mesh object.

![Import to the material slots](https://user-images.githubusercontent.com/7637832/110414597-003c9080-8045-11eb-871b-ce758886c1aa.png)

The addon exports (not only an active material but also) the variants materials, and exports the variants materials configurations as `KHR_materials_variants` extension to the exported glTF.

![Export as KHR_materials_variants extension](https://user-images.githubusercontent.com/7637832/110416635-e43aee00-8048-11eb-92b5-aa74ec41f2f9.png)

## Limitations

Currently the addon allows to set variant materials per a mesh object but it should allow it per a vertex_group of a mesh object similar to that the Blender allows to assign a material per a vertex_group of a mesh object [#4](https://github.com/takahirox/glTF-Blender-IO-materials-variants/issues/4)
