from langchain_community.document_loaders.glue_catalog import GlueCatalogLoader

database_name = "my_database"
profile_name = "my_profile"

loader = GlueCatalogLoader(
    database=database_name,
    profile_name=profile_name,
)

schemas = loader.load()
print(schemas)