import pyzipper
import os

def protect_zip(existing_zip, password):
    base, ext = os.path.splitext(existing_zip)
    output_zip = f"{base}-protected{ext}"  # Append '-protected' before file extension
    
    with pyzipper.AESZipFile(output_zip, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zipf:
        zipf.setpassword(password.encode())

        with pyzipper.AESZipFile(existing_zip, 'r') as original_zip:
            for file in original_zip.namelist():
                zipf.writestr(file, original_zip.read(file))  # Copy files with encryption

    print(f"Password-protected ZIP saved as: {output_zip}")

protect_zip("/mnt/data/Web/movie_site/v2.zip", "(AESZipFile)")
