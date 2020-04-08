import logging

from mic._model_catalog_utils import get_label_from_response, create_request, get_existing_resources
from mic.drawer import print_request, print_choices, show_values_complex, show_values
from mic.file import save
from mic._utils import first_line_new
from mic._mappings import *

COMPLEX_CHOICES = ["select", "add", "edit", "remove"]
ACTION_CHOICES = ["save", "send", "exit"]


def menu_select_existing_resources(variable_selected):
    """
    Menu: Show the existing resources and asks to user the selection
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @return: A resource
    @rtype: dict
    """
    click.echo("Available resources")
    response = get_existing_resources(variable_selected)
    resources = get_label_from_response(response)
    print_choices(resources)
    if click.confirm("Did you find the {}?".format(variable_selected), default=True):
        choice = click.prompt("Select the {}".format(variable_selected),
                              default=1,
                              show_choices=False,
                              type=click.Choice(list(range(1, len(resources) + 1))),
                              value_proc=parse
                              )
        return response[choice - 1].to_dict()
    return None


def menu_select_property(request, mapping):
    """
    Menu: Show the properties by the request
    @param request: Request (modelcatalog spec)
    @type request: dict
    @param mapping: Mapping of the resource
    @type mapping: dict
    @return: the choice
    @rtype: [int, str]
    """
    print_request(request, mapping)
    properties_choices = list(request.keys())
    actions_choices = ["show", "save", "send", "load", "exit"]
    choices = properties_choices + actions_choices
    select_property = click.prompt(
        "Select the property to edit [{}-{}] or [show, save, send, load, exit]".format(1, len(properties_choices)),
        default=1,
        show_choices=False,
        type=click.Choice(list(range(1, len(properties_choices) + 1)) + actions_choices),
        value_proc=parse
    )
    return select_property


def menu_call_actions_complex(request, variable_selected, resource_name, mapping, request_property):
    """
    Asks about the action to take for complex resource (select, add, edit, remove)
    @param request: request
    @type request: dict
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @param resource_name: the resource_name to print it
    @type resource_name: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    @param request_property: the property selected (model spec). For example: has_version
    @type request_property: string
    @return: The action to take: COMPLEX_CHOICES
    @rtype: string
    """
    choices_new = COMPLEX_CHOICES.copy()
    if request[request_property] is None:
        choices_new.remove("edit")
        choices_new.remove("remove")

    choice = click.prompt("Select action:",
                          default=choices_new[0],
                          show_choices=True,
                          type=click.Choice(choices_new),
                          value_proc=parse
                          )
    if choice == COMPLEX_CHOICES[0]:
        call_menu_select_existing_resources(request, variable_selected, resource_name, mapping, request_property)
    elif choice == COMPLEX_CHOICES[1]:
        mapping_create_value_complex(request, variable_selected, mapping, request_property)
    elif choice == COMPLEX_CHOICES[2]:
        menu_edit_resource_complex(request[request_property], variable_selected, mapping)
    elif choice == COMPLEX_CHOICES[3]:
        menu_delete_resource_complex(request[request_property])
    return choice


def menu_delete_resource_complex(request):
    """
    Menu: asks the resource to delete
    @param request: request
    @type request: dict
    """
    labels = get_label_from_response(request)
    print_choices(labels)
    choice = click.prompt("Select the resource to delete",
                          default=1,
                          show_choices=False,
                          type=click.Choice(list(range(1, len(labels) + 1))),
                          value_proc=parse
                          )
    request.pop(choice - 1)


def menu_ask_simple_value(variable_selected, resource_name, mapping, default_value=""):
    """
    Menu: ask the value for simple property
    @param default_value: If the resource has a value, pass it as default value
    @type default_value: [int, string, bool, float]
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @param resource_name: the resource_name to print it
    @type resource_name: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    @return:
    @rtype:
    """
    get_definition(mapping, variable_selected)
    value = click.prompt('{} - {} '.format(resource_name, variable_selected), default=default_value)
    if value:
        return value
    else:
        return None


def menu_push(request):
    pass


def menu_edit_resource_complex(request, variable_selected, mapping):
    """
    Call to the menu to create the resource complex
    @param request: request
    @type request: dict
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    """
    labels = get_label_from_response(request)
    print_choices(labels)
    choice = click.prompt("Select the resource to edit",
                          default=1,
                          show_choices=False,
                          type=click.Choice(list(range(1, len(labels) + 1))),
                          value_proc=parse
                          )
    request_var = get_prop_mapping(mapping, variable_selected)
    call_edit_resource(request, mapping, variable_selected, request_var)


def call_ask_value(request, variable_selected, resource_name, mapping):
    """
    Asks about the value (complex or not)
    @param request: request
    @type request: dict
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @param resource_name: the resource_name to print it
    @type resource_name: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    """
    request_property = get_prop_mapping(mapping, variable_selected)
    click.clear()

    if is_complex(mapping, variable_selected):
        show_values_complex(mapping, request, request_property, variable_selected)
        menu_call_actions_complex(request, variable_selected, resource_name, mapping, request_property)
    else:
        show_values(mapping, request, request_property, variable_selected)
        call_ask_simple_value(request, variable_selected, resource_name, mapping, request_property)


def call_ask_simple_value(request, variable_selected, resource_name, mapping, request_property):
    """
    Call to the menu to set the value for simple resource
    @param request: request
    @type request: dict
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @param resource_name: the resource_name to print it
    @type resource_name: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    @param request_property: the property selected (model spec). For example: has_version
    @type request_property: string
    """
    default_value = request[request_property] if request_property in request and request[request_property] else None
    default_value = default_value[0] if isinstance(default_value, list) else default_value

    value = menu_ask_simple_value(variable_selected, resource_name, mapping[variable_selected],
                                  default_value=default_value)
    if value:
        request[request_property] = [value]


def call_menu_select_existing_resources(request, variable_selected, resource_name, mapping, request_property):
    """
    Call to the menu to select the resource complex
    @param request: request
    @type request: dict
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @param resource_name: the resource_name to print it
    @type resource_name: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    @param request_property: the property selected (model spec). For example: has_version
    @type request_property: string
    """
    value = None
    if select_enable(mapping[variable_selected]):
        sub_resource = menu_select_existing_resources(variable_selected)
        value = sub_resource if sub_resource else mapping_resource_complex(variable_selected, mapping)
    elif not request[request_property]:
        value = mapping_resource_complex(variable_selected, mapping)
    if request[request_property] is None:
        request[request_property] = [value]
    else:
        request[request_property].append(value)


def call_menu_select_property(mapping, resource_name, request=None):
    """
    Method to call the menu to add resource
    @param mapping: Mapping of the resource
    @type mapping: dict
    @param resource_name: the resource_name to print it
    @type resource_name: string
    :param request: request (optionally loaded from file)
    """
    if request is None:
        request = create_request(mapping.values())
    while True:
        click.clear()
        first_line_new(resource_name)
        property_chosen = menu_select_property(request, mapping)
        if handle_actions(request, property_chosen):
            break
        property_model_catalog_selected = list(mapping.keys())[property_chosen - 1]
        call_ask_value(request, property_model_catalog_selected, resource_name=resource_name, mapping=mapping)


def call_edit_resource(request, mapping, resource_name, request_property):
    """
    Call to the menu to edit the resource complex
    @param request: request
    @type request: dict
    @param resource_name: the resource_name to print it
    @type resource_name: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    @param request_property: the property selected (model spec). For example: has_version
    @type request_property: strin
    """
    while True:
        if (request_property == "author") or (request_property == "contributor"):
            mapping = mapping_person
            resource_name = "Person"
        property_chosen = menu_select_property(request[0], mapping)
        if handle_actions(request, property_chosen):
            break
        property_mcat_selected = list(mapping.keys())[property_chosen - 1]
        call_ask_value(request[0], property_mcat_selected, resource_name=resource_name, mapping=mapping)


def mapping_resource_complex(variable_selected, mapping):
    """
    Mapping: maps the variable_select with the Model Catalog Resource
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    """
    prop = mapping[variable_selected]["id"]
    if prop == "has_version":
        return call_menu_select_property(mapping_model_version, SoftwareVersion)
    elif (prop == "author") or (prop == "contributor") or (prop == "has_contact_person"):
        return call_menu_select_property(mapping_person, Person)
    elif prop == "logo":
        return call_menu_select_property(mapping_image, Image)


def mapping_create_value_complex(request, variable_selected, mapping, request_property):
    """
    Call to the menu to create the resource complex
    @param request: request
    @type request: dict
    @param variable_selected: The name of variable selected (mic spec). For example: Versions
    @type variable_selected: string
    @param mapping: Mapping of the resource
    @type mapping: dict
    @param request_property: the property selected (model spec). For example: has_version
    @type request_property: string
    """
    value = mapping_resource_complex(variable_selected, mapping)
    if request[request_property] is None:
        request[request_property] = [value]
    else:
        request[request_property].append(value)


def handle_actions(request, action):
    """
    Verify the choice (menu_select_property) and call the special actions (save, push and exists). If not return False
    @param request: request (modelcatalog spec)
    @type request: dict
    @param action: The choice
    @type action: [str, int]
    @return: True: the special action is done. False: The user is selecting a property, handle the next action.
    @rtype: bool
    """
    if type(action) != str:
        return False
    if action == ACTION_CHOICES[0]:
        save(request)
    elif action == ACTION_CHOICES[1]:
        menu_push(request)
    elif action == ACTION_CHOICES[2]:
        pass
    return True


def parse(value):
    try:
        return int(value)
    except:
        return value
