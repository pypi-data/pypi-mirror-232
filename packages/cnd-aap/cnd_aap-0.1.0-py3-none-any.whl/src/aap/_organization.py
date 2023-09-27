from ._base import Base


class Organization(Base):
    home_path = 'organizations'

    def data(self, name, description=None):
        description = description if description is not None else ''
        return {"name": name, "description": description}
