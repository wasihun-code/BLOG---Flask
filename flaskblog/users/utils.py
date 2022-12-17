import secrets, os
from PIL import Image
from flask import url_for
from flask_mail import Message
from flaskblog import app,  mail

def send_reset_email(user):

    token = user.get_reset_token()
    message = Message(
        "Password reset request", sender="noreply@gmail.com", recipients=[user.email]
    )
    message.body = f"""
        Follow the link bellow to reset your password
        { url_for('users.reset_password', token=token, _external=True) }

        Ignore this message if you didn't request for a password change.
    """
    
    # DEBUGGING PURPOSE
    print("SENDING MESSAGE")
    mail.send(message)


def save_picture(form_picture_data):

    # Grab the file extension from the form data
    _, file_extension = os.path.splitext(form_picture_data.filename)

    # Generate a random file name to avoid filename conflict
    random_file_name = secrets.token_hex(8)

    # Concatenate random file name and file extension
    picture_fn = random_file_name + file_extension

    # extract and store the picture path
    picture_path = os.path.join(app.root_path, "static/profile_pictures/", picture_fn)

    # Input a custom output size
    output_size = (125, 125)

    # Prepare the image to resize: open it
    i = Image.open(form_picture_data)

    # Resize the image
    i.thumbnail(output_size)

    # save the picture on the extracted path
    i.save(picture_path)

    # return the file name later to update it on the database
    return picture_fn
 