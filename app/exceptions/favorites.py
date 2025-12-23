class FavoriteNotFoundException(Exception):
    def __init__(self, favorite_id: int = None, profile_id: int = None, by_profile: bool = False):
        if by_profile and profile_id:
            super().__init__(f"Favorite with profile_id {profile_id} not found")
        else:
            super().__init__(f"Favorite with id {favorite_id} not found")
        self.favorite_id = favorite_id
        self.profile_id = profile_id


class FavoriteAlreadyExistsException(Exception):
    def __init__(self, profile_id: int):
        super().__init__(f"Favorite with profile_id {profile_id} already exists")
        self.profile_id = profile_id