import traceback
from ciocore import conductor_submit
from cioblender.submission_panel import SubmissionPanel

from cioblender.submission_dialog import SubmissionDialog
import bpy

def invoke_submission_dialog(payload):
    """
    Execute the modal submission dialog given nodes.
    """
    submission_dialog = SubmissionDialog(payload)

    result = submission_dialog.exec_()


def submit_job(payload):
    #submitter = SubmissionPanel(bpy.types.Panel)
    #bpy.utils.register_class(SubmissionPanel)

    try:
        #print("Submitting job: ", payload)
        print("upload_paths: ", payload.get("upload_paths"))
        remote_job = conductor_submit.Submit(payload)
        response, response_code = remote_job.main()
    except:
        response = traceback.format_exc()
        response_code = 500
    return {"response": response, "response_code": response_code}
