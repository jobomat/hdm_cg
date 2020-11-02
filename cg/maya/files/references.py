from os import getenv
from os.path import join
import pymel.core as pc
from cg.maya.files.paths import normpath
from cg.maya.utils.names import get_namespace


def load_relative_references(search_path, env_var_name, namespace_map={}):
    starting_dir = pc.workspace.path
    scenes_folder = pc.workspace.fileRules.get("mayaAscii")
    if scenes_folder:
        starting_dir = join(starting_dir, scenes_folder)
    ref_files = pc.fileDialog2(
        caption="Create Reference", fileMode=4, fileFilter="*.ma *.mb",
        startingDirectory=normpath(starting_dir).replace("\\", "/")
    )
    if not ref_files:
        return
    for ref_file in ref_files:
        if normpath(ref_file).startswith(search_path):
            ref_file = ref_file.replace(
                search_path, "${}".format(env_var_name)
            )
        else:
            pc.warning("'{}': Path differs from Env-Var-Path. Path will be absolute.".format(ref_file))
        pc.cmds.file(
            ref_file, r=True, ignoreVersion=True, mergeNamespacesOnClash=False,
            namespace=get_namespace(ref_file, namespace_map)
        )


def change_to_relative(reference, search_path, env_var_name):
    if normpath(reference.path).startswith(search_path):
        reference.replaceWith(
            reference.path.replace(
                search_path, "${}".format(env_var_name)
            )
        )
    else:
        pc.warning(
            "{}'s path differs from path specified in Env-Var '{}'. Not changed.".format(
                reference, env_var_name
            )
        )


class RefChecker():
    def __init__(self, env_var_name, namespace_map={}):
        self.env_var_name = env_var_name
        self.namespace_map = namespace_map
        self.win_id = "ref_checker_window"

    def gui(self):
        self.env_var_path = normpath(getenv(self.env_var_name)).split(";")[0]
        self.project_path = normpath(pc.workspace.path)
        self.cell_height = 30
        self.cw4 = [180, 60, 2, 100]
        self.adj = 3
        self.row_colors = [[0.36, 0.36, 0.36], [0.43, 0.43, 0.43], ]
        self.row_colors2 = [[0.25, 0.25, 0.25], [0.33, 0.33, 0.33], ]
        if pc.window(self.win_id, q=1, exists=1):
            pc.deleteUI(self.win_id)

        with pc.window(self.win_id, title="Reference Checker", wh=[900, 400]) as win:
            with pc.verticalLayout() as self.v:
                with pc.rowLayout(nc=4, h=40) as self.toolbar:
                    pc.text(label="  ")
                    pc.button("Create Relative References", w=150, c=self.create_relative_references)
                    pc.button("All Paths to Relative", w=150, c=self.change_all_paths)
                    pc.button("Refresh Reference List", w=150, c=self.build_reference_list)
                with pc.rowLayout(nc=4, bgc=[0.2, 0.2, 0.2], adj=self.adj,
                                  cw4=self.cw4, h=self.cell_height) as self.table_header_rowLayout:
                    pc.text(label=" Ref", font="boldLabelFont", align="left")
                    pc.text(label=" Path Type", font="boldLabelFont", align="left")
                    pc.text(label=" Unresolved Path", font="boldLabelFont", align="left")
                    pc.text(label="")
                with pc.scrollLayout(childResizable=True) as self.ref_columnLayout:
                    self.build_reference_list()

        win.setWidth(900)
        self.v.attachPosition(self.toolbar, "bottom", 40, 0)
        self.v.attachPosition(self.table_header_rowLayout, "bottom", 80, 0)
        self.v.attachPosition(self.ref_columnLayout, "top", 80, 0)

    def build_reference_list(self, *args):
        self.top_level_references = pc.listReferences()
        self.nested_references = [r for r in pc.listReferences(recursive=True) if r.parent()]
        for child in self.ref_columnLayout.getChildren():
            pc.deleteUI(child)

        with pc.columnLayout(adjustableColumn=True, parent=self.ref_columnLayout):
            for i, ref in enumerate(self.top_level_references):
                ref_resolved_path = normpath(ref.path)
                ref_unresolved_path = normpath(ref.unresolvedPath())
                absolute_path = ref_resolved_path == ref_unresolved_path
                with pc.rowLayout(nc=4, adj=self.adj, cw4=self.cw4, h=self.cell_height,
                                  bgc=self.row_colors[i % 2]):
                    pc.text(label=ref.refNode, h=self.cell_height, align="left")
                    pc.text(label="Absolut" if absolute_path else "Relative", align="left")
                    pc.text(label=ref_unresolved_path, align="left")
                    if absolute_path:
                        pc.button(
                            label="To Relative Path", bgc=[0.5, 0.5, 0.5],
                            c=pc.Callback(self.change_path, ref), w=self.cw4[3],
                            annotation="From '{}' to '${}...'".format(
                                ref_unresolved_path, self.env_var_name
                            )
                        )
                    else:
                        pc.button(
                            label="To Absolute Path", bgc=[0.5, 0.5, 0.5], enable=False,
                            c=pc.Callback(self.change_path, ref), w=self.cw4[3]
                        )
                pc.separator(height=1)
            if self.nested_references:
                pc.text(label="NESTED REFERENCES (NOT EDITABLE)", bgc=[0.2, 0.2, 0.2], h=30)
                pc.separator(height=1)
            for i, ref in enumerate(self.nested_references):
                ref_resolved_path = normpath(ref.path)
                ref_unresolved_path = normpath(ref.unresolvedPath())
                absolute_path = ref_resolved_path == ref_unresolved_path
                with pc.rowLayout(nc=4, adj=self.adj, cw4=self.cw4, h=self.cell_height,
                                  bgc=self.row_colors2[i % 2]):
                    pc.text(label=ref.refNode, h=self.cell_height, align="left")
                    pc.text(label="Absolut" if absolute_path else "Relative", align="left")
                    pc.text(label=ref_unresolved_path, align="left")
                    pc.text(label="")
                pc.separator(height=1)

    def change_path(self, ref):
        change_to_relative(ref, self.env_var_path, self.env_var_name)
        self.build_reference_list(self)

    def change_all_paths(self, *args):
        for ref in self.top_level_references:
            if ref.unresolvedPath().startswith("$"):
                continue
            change_to_relative(ref, self.env_var_path, self.env_var_name)
        self.build_reference_list(self)

    def create_relative_references(self, *args):
        load_relative_references(self.env_var_path, self.env_var_name, self.namespace_map)
        self.build_reference_list(self)
