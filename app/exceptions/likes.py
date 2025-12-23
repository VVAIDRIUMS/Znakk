class LikeNotFoundException(Exception):
    def __init__(self, like_id: int = None, profile_id: int = None, by_profile: bool = False):
        if by_profile and profile_id:
            super().__init__(f"Like with profile_id {profile_id} not found")
        else:
            super().__init__(f"Like with id {like_id} not found")
        self.like_id = like_id
        self.profile_id = profile_id


class LikeAlreadyExistsException(Exception):
    def __init__(self, profile_id: int):
        super().__init__(f"Like with profile_id {profile_id} already exists")
        self.profile_id = profile_id