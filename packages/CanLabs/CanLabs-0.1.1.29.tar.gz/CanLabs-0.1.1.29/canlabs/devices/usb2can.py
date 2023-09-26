"""
MIT License

Permission is hereby granted, free of charge, to Alexandre Meline
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

Copyright (c) 2023 Alexandre Meline

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import subprocess
from canlabs.utils.check_root import check_root

# ../ core
CORE_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# ../../ CanLabs
BUILD = os.path.dirname(CORE_FOLDER)

class Usb2Can:
    """
    Cette classe permet de gérer le pilote USB2CAN. 
    Elle permet de supprimer le pilote USB2CAN, de le télécharger, de le build,
    de charger les modules du pilote USB2CAN et de créer l'interface CAN.

    Elle offre également la possibilité de vérifier si le pilote USB2CAN est présent,
    si le module du pilote USB2CAN est chargé et si l'interface CAN existe.

    params: can_interface_name: (str) Nom de l'interface CAN
    """
    def __init__(self, can_interface_name="can0"):
        if not check_root():
            exit(1)
        self.can_interface_name = can_interface_name # Nom de l'interface CAN

    def delete_usb2can_driver(self) -> bool:
        """
        Supprime le driver folder USB2CAN
        
        return: True si le folder du driver USB2CAN a été supprimé avec succès, False sinon
        """
        try:
            if os.path.exists(os.getcwd() + "/usb2can"):
                subprocess.run(["rm", "-rf", BUILD + "/usb2can"], stdout=subprocess.DEVNULL)
                if os.path.exists(BUILD + "/usb2can"):
                    return False
                else:
                    return True
            return True
        except subprocess.CalledProcessError:
            return False

    def download_usb2can_driver(self) -> bool:
        """
        Télécharge le pilote USB2CAN
        
        return: True si le pilote USB2CAN a été téléchargé avec succès, False sinon
        """
        try:
            # Télécharge le pilote USB2CAN s'il n'existe pas
            if not os.path.exists(os.getcwd() + "/usb2can"):
                subprocess.run(["git", "clone", "https://github.com/8devices/usb2can.git"], stdout=subprocess.DEVNULL)
                if not os.path.exists(BUILD + "/usb2can"):
                    return False
                return True
            else:
                return True
        except subprocess.CalledProcessError:
            return False

    def build_usb2can_driver(self) -> bool:
        """
        Build le pilote USB2CAN
        
        return: True si le pilote USB2CAN a été build avec succès, False sinon
        """
        try:
            # Build le pilote USB2CAN
            # Chemin actuelle d'execution
            os.chdir(os.getcwd() + "/usb2can")
            # Vérifie si le pilote USB2CAN a été build est et dans le kernel
            if os.path.exists("usb_8dev.ko"):
                return True
            subprocess.run(["make"])
            if os.path.exists("usb_8dev.ko"):
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False

    def load_usb2can_module(self) -> bool:
        """
        Charge le module du pilote USB2CAN dans le kernel
        
        return: True si le module du pilote USB2CAN a été chargé avec succès, False sinon
        """
        try:
            os.chdir(BUILD + "/usb2can")
            subprocess.run(["insmod", f"usb_8dev.ko"])
            subprocess.run(["modprobe", "can_raw"], check=True)
            subprocess.run(["modprobe", "can_dev"], check=True)
            # Vérifie si le module du pilote USB2CAN est chargé
            if self.check_usb2can_module():
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False
        
    def delete_usb2can_module(self) -> bool:
        """
        Supprime le module du pilote USB2CAN dans le kernel
        
        return: True si le module du pilote USB2CAN a été supprimé avec succès, False sinon
        """
        try:
            # Vérifie si le module du pilote USB2CAN est chargé
            if not self.check_usb2can_module():
                return True
            subprocess.run(["rmmod", f"usb_8dev.ko"])
            if not self.check_usb2can_module():
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False
        
    def delete_usb2can_interface(self) -> bool:
        """
        Supprime l'interface CAN et le module du driver USB2CAN dans le kernel
        
        return: True si l'interface CAN a été supprimée avec succès, False sinon
        """
        try:
            # Vérifie si l'interface CAN existe
            if not self.can_interface_exist():
                return True
            subprocess.run(["ip", "link", "set", self.can_interface_name, "down"])
            subprocess.run(["ip", "link", "delete", self.can_interface_name])
            if not self.can_interface_exist():
                if self.delete_usb2can_modules():
                    return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False

    def create_usb2can_interface(self, bitrate=1000000, sample_point=0.875) -> bool:
        """
        Crée l'interface CAN
        
        return: True si l'interface CAN a été créée avec succès, False sinon
        """
        # Configure l'interface CAN
        try:
            if self.is_usb2can_present():
                try:
                    subprocess.run(["ip", "link", "set", self.can_interface_name, "up", "type", "can", "bitrate", str(bitrate), "sample-point", str(sample_point)], check=True)
                    return True
                except subprocess.CalledProcessError:
                    return False
            else:
                return False
        except subprocess.CalledProcessError:
            return False
        
    def check_usb2can_module(self) -> bool:
        """
        Vérifie si le module du pilote USB2CAN est chargé

        return: True si le module du pilote USB2CAN est chargé, False sinon
        """
        try:
            # Vérifie si le module du pilote USB2CAN est chargé
            result = subprocess.run(["lsmod"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if "usb_8dev" in result.stdout.decode("utf-8"):
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False
        
    def is_usb2can_present(self) -> bool:
        """
        Vérifie si le périphérique USB2CAN est connecté en USB
        
        return: True si le périphérique USB2CAN est connecté en USB, False sinon
        """
        try:
            # Exécute la commande lsusb pour obtenir la liste des périphériques USB
            lsusb_output = subprocess.check_output(["lsusb"]).decode("utf-8")

            # Recherche la ligne correspondant au périphérique USB2CAN
            if "STMicroelectronics USB2CAN converter" in lsusb_output:
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False
    
    def can_interface_exist(self) -> bool:
        """
        Vérifie si l'interface CAN existe
        
        return: True si l'interface CAN existe, False sinon
        """
        try:
            # Vérifie si l'interface CAN existe
            result = subprocess.run(["ip", "link", "show", self.can_interface_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False
