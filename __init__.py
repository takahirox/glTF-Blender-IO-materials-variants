import bpy
from io_scene_gltf2.blender.exp import gltf2_blender_gather_materials
from io_scene_gltf2.blender.imp.gltf2_blender_material import BlenderMaterial

bl_info = {
    "name" : "glTF KHR_materials_variants IO",
    "author" : "Takahiro Aoyagi",
    "description" : "Addon for glTF KHR_materials_variants extension",
    "blender" : (3, 1, 0),
    "version" : (0, 0, 3),
    "location" : "",
    "wiki_url": "https://github.com/takahirox/glTF-Blender-IO-materials-variants",
    "tracker_url": "https://github.com/takahirox/glTF-Blender-IO-materials-variants/issues",
    "support": "COMMUNITY",
    "warning" : "",
    "category" : "Generic"
}

glTF_extension_name = "KHR_materials_variants"

# Custom hooks. Defined here and registered/unregistered in register()/unregister().
# Note: If other installed addon have custom hooks on the same way at the same places
#       they can be conflicted. Ex: There are two addons A and B which have custom hooks.
#       Imagine A is installed, B is installed, and then A is removed. B is still installed
#       But removing A resets the hooks in unregister().

# The glTF2 importer doesn't provide a hook mechanism for user extensions so
# manually extend a function to import the extension
from io_scene_gltf2.blender.imp.gltf2_blender_node import BlenderNode
orig_create_mesh_object = BlenderNode.create_mesh_object
def patched_create_mesh_object(gltf, vnode):
    obj = orig_create_mesh_object(gltf, vnode)
    create_mesh_object_with_material_variants(obj, gltf, vnode)
    return obj

# Properties

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

# Operators

class AddVariantMaterial(bpy.types.Operator):
    bl_idname = "wm.add_variant_material"
    bl_label = "Add Material Variant"

    def execute(self, context):
        props = context.object.VariantMaterialArrayProperty.value
        props.add()
        return {'FINISHED'}

class RemoveVariantMaterial(bpy.types.Operator):
    bl_idname = "wm.remove_variant_material"
    bl_label = "Remove Material Variant"

    # Set by NodePanel
    index: bpy.props.IntProperty(name="index")

    def execute(self, context):
        props = context.object.VariantMaterialArrayProperty.value
        props.remove(self.index)
        return {'FINISHED'}

# Panels

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

# Register/Unregister

def register():
    BlenderNode.create_mesh_object = patched_create_mesh_object

    bpy.utils.register_class(NodePanel)
    bpy.utils.register_class(VariantMaterialProperties)
    bpy.utils.register_class(VariantMaterialArrayProperty)
    bpy.utils.register_class(AddVariantMaterial)
    bpy.utils.register_class(RemoveVariantMaterial)
    bpy.types.Object.VariantMaterialArrayProperty = bpy.props.PointerProperty(type=VariantMaterialArrayProperty)

def unregister():
    BlenderNode.create_mesh_object = orig_create_mesh_object

    bpy.utils.unregister_class(NodePanel)
    bpy.utils.unregister_class(VariantMaterialProperties)
    bpy.utils.unregister_class(VariantMaterialArrayProperty)
    bpy.utils.unregister_class(AddVariantMaterial)
    bpy.utils.unregister_class(RemoveVariantMaterial)
    del bpy.types.Object.VariantMaterialArrayProperty

# Import

def create_mesh_object_with_material_variants(obj, gltf, vnode):
    if gltf.data.extensions is None or glTF_extension_name not in gltf.data.extensions:
        return

    variant_names = gltf.data.extensions[glTF_extension_name]["variants"]
    pynode = gltf.data.nodes[vnode.mesh_node_idx]
    pymesh = gltf.data.meshes[pynode.mesh]

    variant_materials = obj.VariantMaterialArrayProperty.value
    for primitive in pymesh.primitives:
        if primitive.extensions is None or glTF_extension_name not in primitive.extensions:
            continue
        mappings = primitive.extensions[glTF_extension_name]["mappings"]
        for mapping in mappings:
            variants = mapping["variants"]
            material_index = mapping["material"]
            for variant_index in variants:
                pymaterial = gltf.data.materials[material_index]
                vertex_color = "COLOR_0" if "COLOR_0" in primitive.attributes else None
                if vertex_color not in pymaterial.blender_material:
                    BlenderMaterial.create(gltf, material_index, vertex_color)

                # Add MaterialVariant property
                variant_material = variant_materials.add()
                variant_material.name = variant_names[variant_index]["name"]
                blender_material_name = pymaterial.blender_material[vertex_color]
                blender_material = bpy.data.materials[blender_material_name]
                variant_material.material = blender_material

                # Put material is slot if not there
                # Assume obj is a mesh object. Is this assumption always true?
                mesh = obj.data
                if blender_material_name not in mesh.materials:
                    mesh.materials.append(blender_material)

# Export

# Use glTF-Blender-IO User extension hook mechanism
class glTF2ExportUserExtension:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension

    # Currenlty blender_object in gather_mesh_hook is None
    # So set up the extension in gather_node_hook instead.
    # I assume a mesn is not shared among multiple nodes,
    # Is the assumption always true?
    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.mesh is None:
            return

        # Just in case
        if blender_object.VariantMaterialArrayProperty is None:
            return

        # @TODO: Verify or ensure unique names?

        # Make groups which have the same material
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

        # Make the extension properties from the groups
        # Note: variants property is defined as variant index array in the extension specification
        #       but variant index is unknown yet in this hook because making variant indices
        #       needs to know all variant names by accessing all mesh primitives.
        #       So making variant name array here and replacing it with variant index array
        #       later in custom_gather_gltf_hook.
        mappings = []
        for material in mapping_dict.keys():
            mappings.append({"material": material, "variants": mapping_dict[material]})

        # Assign the extension to primitives.
        # @TODO: Currently assigning the same variants materials configuration to all the primitives
        #        in a mesh but ideally different configuration can be assigned for each primitive.
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

    def gather_gltf_extensions_hook(self, gltf2_object, export_settings):
        meshes = gltf2_object.meshes

        # Get all the variant names from all the meshes
        name_dict = {}
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

        # Now all the variant names are known.
        # So replacing variant name array set in gather_node_hook
        # with variant index array here.
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

        # Set the root extension
        variants = []
        for name in names:
            variants.append({'name': name})
        
        gltf2_object.extensions['KHR_materials_variants'] = {"variants": variants}
