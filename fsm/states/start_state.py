from db_models import ServiceTypes
from . import base_state


class StartState(base_state.BaseState):
    has_entry = False

    async def process(self, context, user, db):
        # TODO: LOG IN FOR MEDICS AND SOCIAL WORKERS

        # TODO: ADD `LANGUAGE` TO SCHEMA (NON-REQUIRED) AND ASSUME USER LANGUAGE WITH IT,
        # TODO: LATER ASK IF USER WANT TO CONTINUE WITH HIS LANGUAGE OR WANT TO CHANGE

        # Download profile pictures
        if context['request']['service_in'] == ServiceTypes.TELEGRAM:
            # TODO: ADD SEPARATE CHECK IN SCHEMA IF FILE IS URL or BYTES
            if context['request']['has_file'] and context['request']['has_image']:
                raise NotImplementedError("Downloading files from telegram is not implemented yet. "
                                          "See `start_state.py`.")
        else:
            # If facebook or else (just url to profile)
            # If file do not exist
            if not self.file_exists(f'user_{user.identity}', 'profile.png'):
                # If request has a file and this file is an image
                if context['request']['has_image']:
                    # TODO: ADD CHECK IF `is_file` or any of `is_{media}` is checked, BUT
                    # TODO: no files -> return(403) with description
                    # Should be only one profile picture
                    url = context['request']['files'][0]['payload']
                    path = await self.download_by_url(url, f'user_{user.identity}', 'profile.png')
                    user.profile_picture = path
        # Edit context to not have file
        context['request']['has_file'] = False
        return base_state.GO_TO_STATE("BasicQuestionState")