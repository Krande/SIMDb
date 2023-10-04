from trame.app import get_server
from trame.widgets import vuetify
from trame.ui.vuetify import SinglePageWithDrawerLayout

server = get_server()
state, ctrl = server.state, server.controller

headers = [
    {"text": "Dessert", "value": "name"},
    {"text": "Calories", "value": "calories"},
    {"text": "Fat (g)", "value": "fat"},
    {"text": "Carbs (g)", "value": "carbs"},
    {"text": "Protein (g)", "value": "protein"},
    {"text": 'Actions', "value": 'actions'},
]

desserts = [
    {"name": "Frozen Yogurt", "calories": 159, "fat": 6.0, "carbs": 24, "protein": 4.0},
    {"name": "Ice cream sandwich", "calories": 237, "fat": 9.0, "carbs": 37, "protein": 4.3},
    {"name": "Eclair", "calories": 262, "fat": 16.0, "carbs": 23, "protein": 6.0},
    {"name": "Cupcake", "calories": 305, "fat": 3.7, "carbs": 67, "protein": 4.3},
    {"name": "Gingerbread", "calories": 356, "fat": 16.0, "carbs": 49, "protein": 3.9},
]

state.editedItem = {
    "name": "",
    "calories": 0,
    "fat": 0.0,
    "carbs": 0,
    "protein": 0.0
}

table = {
    "headers": ("headers", headers),
    "items": ("rows", desserts),
    "v_model": ("selection", []),
}


def handle_click(item):
    print("Item:", item)


with SinglePageWithDrawerLayout(server) as layout:
    with layout.content:
        with vuetify.VDataTable(**table) as data_table:
            with vuetify.Template(v_slot_top=True):
                with vuetify.VToolbar(flat=True):
                    vuetify.VToolbarTitle(children=['Edit'])
                    vuetify.VDivider(class_="mx-4", inset=True, vertical=True)
                    vuetify.VSpacer()

                    with vuetify.VDialog(v_model=("dialog", False), max_width="500px") as dialog:
                        with vuetify.Template(v_slot_activator="{ on, attrs }"):
                            vuetify.VBtn(
                                color="primary",
                                dark=True,
                                class_="mb-2",
                                v_bind="attrs",
                                v_on="on",
                                children=["New Item"]
                            )

                        with vuetify.VCard():
                            vuetify.VCardTitle(children=['New entry'])
                            vuetify.VCardText()
                            with vuetify.VContainer():
                                with vuetify.VRow():
                                    # Add v-text-field for each item property
                                    for prop, label in [
                                        ("editedItem.name", "Dessert name"),
                                        ("editedItem.calories", "Calories"),
                                        ("editedItem.fat", "Fat (g)"),
                                        ("editedItem.carbs", "Carbs (g)"),
                                        ("editedItem.protein", "Protein (g)")
                                    ]:
                                        with vuetify.VCol(cols="12", sm="6", md="4"):
                                            vuetify.VTextField(
                                                v_model=(prop,),
                                                label=label
                                            )

                            with vuetify.VCardActions():
                                vuetify.VSpacer()
                                vuetify.VBtn(color="blue darken-1", text=True, children=["Cancel"])  # click="close",
                                vuetify.VBtn(color="blue darken-1", text=True, children=["Save"])  # click="save",

                    with vuetify.VDialog(v_model=("dialogDelete", False), max_width="500px") as delete_dialog:
                        with vuetify.VCard():
                            vuetify.VCardTitle(children=[("Are you sure you want to delete this item?")])
                            with vuetify.VCardActions():
                                vuetify.VSpacer()
                                vuetify.VBtn(color="blue darken-1", text=True,
                                             children=["Cancel"])  # click="closeDelete" click =handle_click
                                vuetify.VBtn(color="blue darken-1", text=True,
                                             children=["OK"])  # click="deleteItemConfirm"
                                vuetify.VSpacer()

            with vuetify.Template(
                    slot_actions="{ item }",
                    __properties=[("slot_actions", "v-slot:item.actions")],
            ):
                vuetify.VIcon("mdi-pencil", small=True, classes="mr-2", click=(handle_click, "[$event]"))
                vuetify.VIcon("mdi-delete", small=True, classes="mr-2", click=(handle_click, "[$event]"))

if __name__ == "__main__":
    server.start(port=5000)
