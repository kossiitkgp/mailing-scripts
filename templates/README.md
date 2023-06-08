### Templates

Things to keep in mind regarding templates:

- First line is the subject for the mail.
- Mail body and subject __are and must__ be separated by an empty new line.
- The email column must be the 2nd column(if the counting starts from 1) in the csv file, it is fixed because 99% of the time this is how it's gonna be.
- Templates are by default stored in `./templates/` and csv must be stored in a folder as `./csv/`, hence no need to mention them again while specifying the location, just speciy the location after these default folders.
- Use HTML syntax to format the mail body.
