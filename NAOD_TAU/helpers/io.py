from coffea.nanoevents import NanoEventsFactory, NanoAODSchema


def build_iteritems_options(filter_name=None):
    if filter_name is None:
        return {}
    return {"filter_name": filter_name}


def load_events(file_path, tree_name="Events", filter_name=None):
    iteritems_options = build_iteritems_options(filter_name)
    factory = NanoEventsFactory.from_root(
        {file_path: tree_name},
        schemaclass=NanoAODSchema,
        iteritems_options=iteritems_options,
    )
    return factory.events()
