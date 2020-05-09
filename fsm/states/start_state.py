from server_logic.definitions import Context
from db_models import ServiceTypes, User
from . import base_state


class StartState(base_state.BaseState):
    has_entry = False

    async def process(self, context: Context, user: User, db):
        # TODO: LOG IN FOR MEDICS AND SOCIAL WORKERS

        # TODO: ADD `LANGUAGE` TO SCHEMA (NON-REQUIRED) AND ASSUME USER LANGUAGE WITH IT,
        # TODO: LATER ASK IF USER WANT TO CONTINUE WITH HIS LANGUAGE OR WANT TO CHANGE

        # Download profile pictures
        if context['request']['service_in'] == ServiceTypes.TELEGRAM:
            # TODO: ADD SEPARATE CHECK IN SCHEMA IF FILE IS URL or BYTES
            # If request from telegram -> we can't download images currently from there
            if context['request']['has_file'] and context['request']['has_image']:
                raise NotImplementedError("Downloading files from telegram is not implemented yet. "
                                          "See `start_state.py`.")
        # @Important: If facebook or else (just url to profile)
        else:
            # If profile image file do not exist yet
            if not self.exists(f"user_{user['identity']}", 'profile.png'):
                # If request has a file and this file is an image
                if context['request']['has_image']:
                    # TODO: ADD CHECK IF `is_file` or any of `is_{media}` is checked, BUT
                    # TODO: no files -> return(403) with description
                    # Should be only one profile picture
                    url = context['request']['files'][0]['payload']
                    # Downloading file and getting path to the file
                    path = await self.download_by_url(url, f"user_{user['identity']}", filename='profile.png')
                    # Assign value to the user picture path
                    user['files']['profile_picture'] = path
        # Edit context to not have file
        context['request']['has_file'] = False
        return base_state.GO_TO_STATE("BasicQuestionState")