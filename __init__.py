import bpy
from io_scene_gltf2.blender.exp import gltf2_blender_gather_materials

bl_info = {
    "name" : "glTF KHR_materials_variants IO",
    "author" : "Takahiro Aoyagi",
    "description" : "Add on for glTF KHR_materials_variants extension",
    "blender" : (2, 91, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "wiki_url": "https://github.com/takahirox/glTF-Blender-IO-materials-variants",
    "tracker_url": "https://github.com/takahirox/glTF-Blender-IO-materials-variants/issues",
    "support": "COMMUNITY",
    "warning" : "",
    "category" : "Generic"
}

glTF_extension_name = "KHR_materials_variants"

# gather_gltf_hook does not expose the info we need, make a custom hook for now
# ideally we can resolve this upstream somehow https://github.com/KhronosGroup/glTF-Blender-IO/issues/1009
from io_scene_gltf2.blender.exp import gltf2_blender_export
from io_scene_gltf2.io.exp.gltf2_io_user_extensions import export_user_extensions
orig_gather_gltf = gltf2_blender_export.__gather_gltf
def patched_gather_gltf(exporter, export_settings):
    orig_gather_gltf(exporter, export_settings)
    export_user_extensions('custom_gather_gltf_hook', export_settings, exporter._GlTF2Exporter__gltf)

class VariantMaterialProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        description="Variant material name"
    )
    material: bpy.props.PointerProperty(
        name="Material",
        description='Variant material',
        type=bpy.types.Material
    )

class VariantMaterialArrayProperty(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name="value", type=VariantMaterialProperties)

class AddVariantMaterial(bpy.types.Operator):
    bl_idname = "wm.add_variant_material"
    bl_label = "Add Material Variant"

    def execute(self, context):
        props = context.object.VariantMaterialArrayProperty.value
        prop = props.add()
        return {'FINISHED'}

class RemoveVariantMaterial(bpy.types.Operator):
    bl_idname = "wm.remove_variant_material"
    bl_label = "Remove Material Variant"

    index: bpy.props.IntProperty(name="index")

    def execute(self, context):
        props = context.object.VariantMaterialArrayProperty.value
        props.remove(self.index)
        return {'FINISHED'}

def register():
    gltf2_blender_export.__gather_gltf = patched_gather_gltf

    bpy.utils.register_class(NodePanel)
    bpy.utils.register_class(VariantMaterialProperties)
    bpy.utils.register_class(VariantMaterialArrayProperty)
    bpy.utils.register_class(AddVariantMaterial)
    bpy.utils.register_class(RemoveVariantMaterial)
    bpy.types.Scene.VariantMaterialProperties = bpy.props.PointerProperty(type=VariantMaterialProperties)
    bpy.types.Scene.VariantMaterialArrayProperty = bpy.props.PointerProperty(type=VariantMaterialArrayProperty)
    bpy.types.Object.VariantMaterialArrayProperty = bpy.props.PointerProperty(type=VariantMaterialArrayProperty)

def unregister():
    gltf2_blender_export.__gather_gltf = orig_gather_gltf

    bpy.utils.unregister_class(NodePanel)
    bpy.utils.unregister_class(VariantMaterialProperties)
    bpy.utils.unregister_class(VariantMaterialArrayProperty)
    bpy.utils.unregister_class(AddVariantMaterial)
    bpy.utils.unregister_class(RemoveVariantMaterial)
    del bpy.types.Scene.VariantMaterialProperties
    del bpy.types.Scene.VariantMaterialArrayProperty
    del bpy.types.Object.VariantMaterialArrayProperty

class NodePanel(bpy.types.Panel):
    bl_label = 'Variants Materials'
    bl_idname = "NODE_PT_variants"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        props = context.object.VariantMaterialArrayProperty.value
        for i, prop in enumerate(props):
            remove_operator = layout.operator(
                "wm.remove_variant_material",
                text="",
                icon="X"
            )
            remove_operator.index = i
            layout.prop(prop, 'name')
            layout.prop(prop, 'material')
            layout.separator()
        layout.operator(
            "wm.add_variant_material",
            text="Add Variant Material",
            icon="ADD"
        )

class glTF2ExportUserExtension:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension

    # Currenlty blender_object in gather_mesh_hook is None
    # So set up the extension in gather_node_hook instead.
    # I assume a mesn is not shared among multiple nodes,
    # Is the assumption true?
    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.mesh is None:
            return

        # Just in case
        if blender_object.VariantMaterialArrayProperty is None:
            return

        # @TODO: Verify unique names?

        variant_materials = blender_object.VariantMaterialArrayProperty.value
        mapping_dict = {}
        for variant_material in variant_materials:
            name = variant_material.name
            material = variant_material.material
            if not name or material is None:
                continue
            material = gltf2_blender_gather_materials.gather_material(
                material,
                export_settings,
            )
            if material is None:
                continue
            if material not in mapping_dict:
                mapping_dict[material] = []
            mapping_dict[material].append(name)

        if not mapping_dict:
            return

        mappings = []
        for material in mapping_dict.keys():
            mappings.append({"material": material, "variants": mapping_dict[material]})

        mesh = gltf2_object.mesh
        primitives = mesh.primitives
        for primitive in primitives:
            if primitive.extensions is None:
                primitive.extensions = {}
            primitive.extensions[glTF_extension_name] = self.Extension(
                name=glTF_extension_name,
                extension={"mappings": mappings},
                required=False
            )

    def custom_gather_gltf_hook(self, gltf2_object, export_settings):
        name_dict = {}
        meshes = gltf2_object.meshes

        for mesh in meshes:
            primitives = mesh.primitives
            for primitive in primitives:
                if primitive.extensions is None or glTF_extension_name not in primitive.extensions:
                    continue
                mappings = primitive.extensions[glTF_extension_name]["mappings"]
                for mapping in mappings:
                    variants = mapping["variants"]
                    for name in variants:
                        name_dict[name] = True

        if not name_dict:
            return

        names = list(name_dict.keys())
        for mesh in meshes:
            primitives = mesh.primitives
            for primitive in primitives:
                if primitive.extensions is None or glTF_extension_name not in primitive.extensions:
                    continue
                mappings = primitive.extensions[glTF_extension_name]["mappings"]
                for mapping in mappings:
                    variants = mapping["variants"]
                    new_variants = []
                    for name in variants:
                        new_variants.append(names.index(name))
                    mapping["variants"] = new_variants

        variants = []
        for name in names:
            variants.append({'name': name})
        
        gltf2_object.extensions['KHR_materials_variants'] = {"variants": variants}
