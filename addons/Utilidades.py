import subprocess
import sys
import os
import glob
import requests
import zipfile
import shutil
import json
import requests
from PIL import Image
from io import BytesIO
import urllib.request

RGB = [(0, 255, 0), (0, 128, 255), (255, 0, 255)]

def prueba():
    filename = "addons/Branchutil.addon"
    url = "https://www.dropbox.com/scl/fo/cjkos3x5ewmxtznr689i0/ADsnCOWvzaeLzGGi8FylBkI?rlkey=k8hmfznh4j3w2xt4oea2vecps&st=fnxqxcqv&dl=1"
    temp_zip = "addons/temp.zip"  
    with open(filename, "r") as file:
        content = file.read()
    if "a_version 1.3" not in content:
        response = requests.get(url)
        with open(temp_zip, "wb") as file:
            file.write(response.content)
        with zipfile.ZipFile(temp_zip, "r") as zip_ref:
            zip_ref.extractall("addons") 
            extracted_files = zip_ref.namelist()
            for file_name in extracted_files:
                if file_name.endswith("Branchutil.addon"):
                    os.rename(os.path.join("addons", file_name), filename)
        os.remove(temp_zip)
        files = os.listdir('.')
        python_files = [file for file in files if file.endswith(".py")]
        for python_file in python_files:
                file_path = os.path.join('.', python_file)
                subprocess.run(['python', file_path])
prueba()

def run_command(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e


def gradient_text(text, colors):
    length = len(text)
    num_colors = len(colors)
    result = ""
    for i, char in enumerate(text):
        color_index = (i * (num_colors - 1)) // length
        t = (i * (num_colors - 1)) / length - color_index
        color1 = colors[color_index]
        color2 = colors[color_index + 1] if color_index + 1 < num_colors else colors[color_index]
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        result += f'\033[38;2;{r};{g};{b}m{char}'
    return result + '\033[0m'

def force_push(branch_name, commit):
    print(gradient_text(f"Realizando push forzado en la rama {branch_name}", [(0, 255, 0), (0, 128, 255)]))
    try:
        run_command(["git", "update-ref", f"refs/heads/{branch_name}", commit])
        run_command(["git", "push", "--force", "origin", branch_name])
        print(gradient_text(f"Push forzado realizado con éxito en la rama {branch_name}.", [(0, 255, 0), (0, 128, 255)]))
    except subprocess.CalledProcessError as e:
        print(gradient_text(f"Error en el push forzado: {e.stderr}", [(255, 0, 0), (255, 128, 0)]))
        sys.exit(1)

def branch():
    os.chdir(f"{glob.glob('/workspaces/*')[0]}/")
    os.system("cd /workspaces/*/")

    new_branch_name = "Minecraft_branch"

    print(gradient_text("Obteniendo la URL del repositorio remoto", [(0, 255, 0), (0, 128, 255)]))
    repo_url = run_command(["git", "remote", "-v"])

    print(gradient_text(f"Eliminando la rama remota", [(0, 255, 0), (0, 128, 255)]))
    run_command(["git", "push", "origin", "--delete", new_branch_name])

    print(gradient_text(f"Eliminando la rama local", [(0, 255, 0), (0, 128, 255)]))
    os.system(f"git branch -D {new_branch_name}")

    run_command(["git", "rm", "-r", "--cached", "."])
    os.system(f"git checkout -b {new_branch_name}")

    archivos_excluidos = []

    for root, _, files in os.walk('servidor_minecraft'):
        for file in files:
            archivo = os.path.join(root, file)
            tamaño = os.path.getsize(archivo)
            if tamaño < 100 * 1024 * 1024:  
                run_command(["git", "add", "--force", archivo])
            else:
                archivos_excluidos.append(archivo)

    for root, _, files in os.walk('addons'):
        for file in files:
            archivo = os.path.join(root, file)
            tamaño = os.path.getsize(archivo)
            if tamaño < 100 * 1024 * 1024:  
                run_command(["git", "add", "--force", archivo])
            else:
                archivos_excluidos.append(archivo)

    configuracion_json = 'configuracion.json'
    tamaño = os.path.getsize(configuracion_json)
    if tamaño < 100 * 1024 * 1024:
        run_command(["git", "add", "--force", configuracion_json])
    else:
        archivos_excluidos.append(configuracion_json)

    commit_tree = run_command(["git", "write-tree"])
    commit_message = "Branch para guardar tu server_minecraft"
    commit = run_command(["git", "commit-tree", commit_tree, "-m", commit_message])

    print(gradient_text("Realizando push", [(0, 255, 0), (0, 128, 255)]))
    force_push(new_branch_name, commit)

    user_name, repo_name = repo_url.split('/')[-2], repo_url.split('/')[-1].replace('.git', '')
    zip_url = f"https://codeload.github.com/{user_name}/{repo_name}/zip/refs/heads/{new_branch_name}".replace(" (push)", "")
    os.system("clear")
    print(gradient_text(f"\nBranch creado/actualizado localmente: {new_branch_name}\nEnlace al branch para descargar en ZIP: {zip_url}", [(0, 255, 0), (0, 128, 255)]))
    url_data = {"Enlace_a_copiar": zip_url}

    with open('addons/url-del-branch.json', 'w') as url_file:
        json.dump(url_data, url_file, indent=4)
        
    if archivos_excluidos:
        print(gradient_text("\nLos siguientes archivos no fueron añadidos al branch debido a que superan los 100MB:", [(255, 0, 0), (255, 128, 0)]))
        for archivo in archivos_excluidos:
            print(archivo)

    input(gradient_text("\nPresiona cualquier tecla para continuar...", [(0, 255, 0), (0, 128, 255)]))
    sys.exit(0)
    
def download_and_extract_zip(url, extract_to):
    local_zip_file = "repo.zip"
    
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_zip_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with zipfile.ZipFile(local_zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    finally:
        if os.path.exists(local_zip_file):
            os.remove(local_zip_file)

def link():
    zip_url2 = input(gradient_text("Introduce el enlace directo del archivo ZIP: ",[(0, 255, 0), (0, 128, 255)])).strip()
    
    temp_dir = "temp_extract"
    os.makedirs(temp_dir, exist_ok=True)
    
    download_and_extract_zip(zip_url2, temp_dir)

    extracted_dir = os.listdir(temp_dir)[0]
    extracted_path = os.path.join(temp_dir, extracted_dir)
    items_to_move = ['addons', 'servidor_minecraft', 'configuracion.json']
    
    for item in items_to_move:
        source_path = os.path.join(extracted_path, item)
        if os.path.exists(source_path):
            target_path = os.path.join(os.getcwd(), item)
            
            if os.path.exists(target_path):
                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                else:
                    os.remove(target_path)
            
            shutil.move(source_path, target_path)
    shutil.rmtree(temp_dir)

    print(gradient_text("\n¡Repositorio descargado y extraído exitosamente!",[(0, 255, 0), (0, 128, 255)]))
    print(gradient_text("\nDirectorio actualizado con el contenido del archivo ZIP.",[(0, 255, 0), (0, 128, 255)]))
    sys.exit(0)

def DescargaDropbox():
    print(gradient_text("¡Los Modpacks están en fase experimental!", [(0, 255, 0), (0, 128, 255)]))
    url = input(gradient_text(f"\nIngrese la URL del Respaldo/Modpack: ", [(0, 255, 0), (0, 128, 255)])).strip()
    dest_folder = "servidor_minecraft"

    if "dropbox" in url and url.endswith('0'):
        url = url[:-1] + '1'

    download_folder = "descargas"
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    print(gradient_text(f"\nDescargando archivos...", RGB))
    local_filename = os.path.join(download_folder, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    temp_extract_folder = os.path.join(download_folder, "temp_extract")
    if not os.path.exists(temp_extract_folder):
        os.makedirs(temp_extract_folder)
    with zipfile.ZipFile(local_filename, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_folder)
    extracted_items = os.listdir(temp_extract_folder)
    
    if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_extract_folder, extracted_items[0])):
        single_folder_path = os.path.join(temp_extract_folder, extracted_items[0])
        for item in os.listdir(single_folder_path):
            s = os.path.join(single_folder_path, item)
            d = os.path.join(dest_folder, item)
            if os.path.exists(d):
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    elif all(os.path.exists(os.path.join(temp_extract_folder, folder)) for folder in ["data"]):
        target_folder = os.path.join(dest_folder, "world")
        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        for item in os.listdir(temp_extract_folder):
            s = os.path.join(temp_extract_folder, item)
            d = os.path.join(target_folder, item)
            if os.path.exists(d):
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    elif all(os.path.exists(os.path.join(temp_extract_folder, folder)) for folder in ["bStats"]):
        target_folder = os.path.join(dest_folder, "plugins")      

        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        for item in os.listdir(temp_extract_folder):
            s = os.path.join(temp_extract_folder, item)
            d = os.path.join(target_folder, item)
            if os.path.exists(d):
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    else:
        for item in os.listdir(temp_extract_folder):
            s = os.path.join(temp_extract_folder, item)
            d = os.path.join(dest_folder, item)
            if os.path.exists(d):
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    shutil.rmtree(temp_extract_folder)
    os.remove(local_filename)
    print(gradient_text(f"Todos los archivos se han movido a {dest_folder}", [(0, 255, 0), (0, 128, 255)]))
    input(gradient_text("\nPresiona cualquier tecla para continuar...", [(0, 255, 0), (0, 128, 255)]))
    sys.exit(0)

def Img_Url():
    os.system("clear")
    img_url = input(gradient_text("Introduce el URL de la imagen: ", [(0, 255, 0), (0, 128, 255)]))

    if "dropbox" in url and url.endswith('0'):
        url = url[:-1] + '1'

    output_dir = 'servidor_minecraft'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    download_link = img_url
    response = requests.get(download_link)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))
    img = img.resize((64, 64), Image.LANCZOS)

    img.save(os.path.join(output_dir, 'server-icon.png'))
    
    print(gradient_text("Imagen transformada a server icon", [(0, 255, 0), (0, 128, 255)]))
    input(gradient_text("\nPresiona cualquier tecla para continuar...", [(0, 255, 0), (0, 128, 255)]))
    sys.exit(0)

def instalar_fabric():
    mc_version = input(gradient_text("Ingrese la versión de Minecraft que desea instalar: ", [(0, 255, 0), (0, 128, 255)]))
    fabric_version = input(gradient_text("Ingrese la versión de Fabric que desea instalar: ", [(0, 255, 0), (0, 128, 255)]))
    
    install_dir = "servidor_minecraft"
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    fabric_installer_url = f"https://meta.fabricmc.net/v2/versions/loader/{mc_version}/{fabric_version}/1.0.1/server/jar"
    fabric_installer_path = os.path.join(install_dir, "fabric-server-launch.jar")
    print(gradient_text("Descargando el instalador de Fabric...", [(0, 255, 0), (0, 128, 255)]))
    urllib.request.urlretrieve(fabric_installer_url, fabric_installer_path)

    config_path = "configuracion.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
        config["server_version"] = mc_version
        config["server_type"] = "fabric"
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)    
    eula_path = os.path.join(install_dir, "eula.txt")
    with open(eula_path, 'w') as eula_file:
        eula_file.write("eula=true\n")
    print(gradient_text("Instalando Fabric...", [(0, 255, 0), (0, 128, 255)]))
    os.chdir(install_dir)
    subprocess.run(["java", "-jar", "fabric-server-launch.jar", "--installServer"], check=True)

import os
import json
import requests

def get_current_branch():
    branch_name = os.popen('git branch --show-current').read().strip()
    print(f"Rama actual: {branch_name}")
    return branch_name

def repo_exists(token, account_name, repo_name):
    url = f"https://api.github.com/repos/{account_name}/{repo_name}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def create_repo(token, account_name, repo_name, repo_private):
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {token}"}
    data = {
        "name": repo_name,
        "private": repo_private
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("Repositorio creado con éxito.")
    else:
        print(f"Error al crear el repositorio: {response.status_code}")
        print(response.json())

def repo():
    print(gradient_text("Sólo es necesario una vez por codespace :)", [(0, 255, 0), (0, 128, 255)]))
    token = input(gradient_text("Introduce tu token de acceso personal de GitHub: ", [(0, 255, 0), (0, 128, 255)]))
    repo_name = "Minecraft_branch"
    repo_private = False
    account_name = input(gradient_text("Introduce el nombre de la cuenta de GitHub donde deseas usar el repositorio: ", [(0, 255, 0), (0, 128, 255)]))

    if repo_exists(token, account_name, repo_name):
        os.system("clear")
        branch()
    else:
        print(gradient_text("El repositorio no existe. Creando un nuevo repositorio.", [(0, 255, 0), (0, 128, 255)]))
        create_repo(token, account_name, repo_name, repo_private)
        os.system('git init')
        os.system('git add .')
        os.system('git commit -m "Primer commit desde Codespace"')
        os.system("clear")
        branch()