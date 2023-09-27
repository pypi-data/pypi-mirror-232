from ._base import Base


class Host(Base):
    home_path = 'hosts'

    def data(self, name, inventory_id, description=None, variables={}):
        description = description if description is not None else ''
        return {
            "name": name,
            "description": description,
            "inventory": inventory_id,
            "variables": variables,
            "instance_id": "",
            "enable": True
        }
