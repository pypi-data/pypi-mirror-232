from ._base import Base


class Team(Base):
    home_path = 'teams'

    def data(self, name, organization_id, description=None):
        description = description if description is not None else ''
        return {"name": name, "description": description, "organization": organization_id}
