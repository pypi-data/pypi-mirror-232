from ._base import Base


class Inventory(Base):
    home_path = 'inventories'

    def data(self, name, organization_id, description=None, variables={}):
        description = description if description is not None else ''
        return {"name": name, "description": description, "organization": organization_id, "variables": variables, "kind": ""}
