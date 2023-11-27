import twain
# First, you'll need to instantiate the SourceManager class.
# Assume `twain` is the module name where the `SourceManager` class resides.
source_manager = twain.SourceManager(parent_window=0)

# Then, you can get the list of available sources using the `source_list` property.
available_sources = source_manager.source_list

# Print or otherwise use the list of available sources.
print("Available TWAIN devices:")
for idx, source in enumerate(available_sources):
    print(f"{idx + 1}. {source}")
