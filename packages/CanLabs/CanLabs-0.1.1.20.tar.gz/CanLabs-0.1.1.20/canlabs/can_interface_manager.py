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
import subprocess
import argparse
from canlabs.devices.usb2can import Usb2Can
from canlabs.utils.colors import TerminalColors
from canlabs.utils.check_root import check_root

class CANInterfaceManager:
    """
    Cette classe permet de gérer l'interface CAN.

    USB2CAN doit être connecté en USB pour pouvoir créer l'interface CAN.
    Elle permet de supprimer le pilote USB2CAN, de le télécharger, de le build,
    de charger les modules du pilote USB2CAN et de créer l'interface CAN.
    """
    def __init__(self, can_interface_name: str ="can0", sample_point: float =0.875, bitrate:int =1000000):
        # If not root, exit
        if not check_root():
            exit(1)
        self.can_interface_name = can_interface_name
        self.sample_point = sample_point
        self.bitrate = bitrate
        self.usb2can = Usb2Can()
        
    def can_interface_exist(self):
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

    def create_usb2can_interface(self):
        """
        Créer l'interface CAN en fonction des conditions actuelles:
        
        Si USB2CAN est connecté, en usb:
            - Supprime le dossier du driver USB2CAN s'il existe dans le repertoire "build"
            - Supprime le module du driver USB2CAN s'il existe dans le kernel
            - Télécharge le pilote USB2CAN
            - Build le pilote USB2CAN
            - Charge le module du pilote USB2CAN
            - Crée l'interface CAN
        """
        usb2can_manager = Usb2Can(can_interface_name=self.can_interface_name)

        # Si USB2CAN est conecté, en usb
        if usb2can_manager.is_usb2can_present():
            print(TerminalColors.GREEN + "USB2CAN est connecté en USB." + TerminalColors.RESET)

            # Supprime le pilote USB2CAN s'il existe
            if usb2can_manager.delete_usb2can_driver():
                print(TerminalColors.GREEN + "Le pilote USB2CAN a été supprimé avec succès." + TerminalColors.RESET)

            # Supprime le pilote USB2CAN
            if usb2can_manager.delete_usb2can_module():
                print(TerminalColors.GREEN + "Le module du pilote USB2CAN a été supprimé avec succès." + TerminalColors.RESET)

            # Télécharge le pilote USB2CAN
            if usb2can_manager.download_usb2can_driver():
                print(TerminalColors.GREEN + "Le pilote USB2CAN a été téléchargé avec succès." + TerminalColors.RESET)
            
            # Build le pilote USB2CAN
            if usb2can_manager.build_usb2can_driver():
                print(TerminalColors.GREEN + "Le pilote USB2CAN a été build avec succès." + TerminalColors.RESET)
            
            # Charge le module du pilote USB2CAN
            if usb2can_manager.load_usb2can_module():
                print(TerminalColors.GREEN + "Le module du pilote USB2CAN a été chargé avec succès." + TerminalColors.RESET)
            
            # Crée l'interface CAN
            if usb2can_manager.create_usb2can_interface(sample_point=self.sample_point, bitrate=self.bitrate):
                print(TerminalColors.GREEN + "L'interface CAN a été créée avec succès." + TerminalColors.RESET)
                return True
            else:
                print(TerminalColors.RED + "L'interface CAN n'a pas pu être créée." + TerminalColors.RESET)
                return False  
        else:
            print(TerminalColors.RED + "USB2CAN n'est pas connecté en USB." + TerminalColors.RESET)
            return False
        
    def delete_usb2can_interface(self):
        """
        Supprime l'interface CAN
        """
        try:
            # Supprime l'interface CAN
            subprocess.run(["ip", "link", "delete", self.can_interface_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

