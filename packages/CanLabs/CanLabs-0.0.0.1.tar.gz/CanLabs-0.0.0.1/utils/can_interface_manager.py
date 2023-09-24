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
import os
from colors import TerminalColors

BUILD = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class CANInterfaceManager:
    def __init__(self, can_interface_name="can0"):
        self.can_interface_name = can_interface_name

    def check_root(self):
        # Vérifie si l'utilisateur est root
        if os.geteuid() != 0:
            print(TerminalColors.RED + "Vous devez être root pour exécuter ce script." + TerminalColors.RESET)
            return False

    def download_usb2can_driver(self):
        # Vérifie si le dossier du pilote USB2CAN est présent
        if not os.path.exists(BUILD + "/usb2can"):
            # Si le dossier n'est pas présent, télécharge le pilote USB2CAN
            print(TerminalColors.YELLOW + "Téléchargement du pilote USB2CAN..." + TerminalColors.RESET)
            subprocess.run(["git", "clone", "https://github.com/8devices/usb2can.git"])
            print(TerminalColors.GREEN + "Le pilote USB2CAN a été téléchargé avec succès." + TerminalColors.RESET)

    def kill_can_interface(self):
        # Vérifie si l'interface CAN existe et la désactive si nécessaire
        if self.check_can_interface():
            subprocess.run(["ip", "link", "set", self.can_interface_name, "down"])
            subprocess.run(["rmmod", "usb_8dev"])
            print(TerminalColors.GREEN + "Interface CAN supprimée avec succès." + TerminalColors.RESET)

    def check_can_interface(self):
        # Vérifie si l'interface CAN existe
        result = subprocess.run(["ip", "link", "show", self.can_interface_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print(TerminalColors.GREEN + f"L'interface CAN: {self.can_interface_name} existe." + TerminalColors.RESET)
            return True
        else:
            print(TerminalColors.YELLOW + f"L'interface CAN: {self.can_interface_name} n'existe pas." + TerminalColors.RESET)
            return False

    def create_can_interface(self, bitrate: int =1000000, sample_point :float =0.875):
        # Change le répertoire vers le dossier du pilote USB2CAN
        os.chdir(BUILD + "/usb2can")
        
        # Build le pilote USB2CAN
        subprocess.run(["make"])
        
        # Charge les modules nécessaires s'ils ne sont pas déjà chargés
        subprocess.run(["modprobe", "can_raw"])
        subprocess.run(["modprobe", "can_dev"])

        # Vérifie si le module usb_8dev.ko existe
        if not os.path.exists("usb_8dev.ko"):
            print(TerminalColors.RED + "Le module usb_8dev.ko n'existe pas." + TerminalColors.RESET)
            exit()

        # Charge le module du pilote USB2CAN
        subprocess.run(["insmod", f"usb_8dev.ko"])

        # Crée l'interface CAN avec des paramètres appropriés
        subprocess.run(["ip", "link", "set", self.can_interface_name, "up", "type", "can", "bitrate", str(bitrate), "sample-point", str(sample_point)])
        print(TerminalColors.GREEN + "Interface CAN créée avec succès." + TerminalColors.RESET)

    def manage_can_interface(self):
        # Vérifie si l'utilisateur est root
        self.check_root()

        # Si l'interface CAN existe, la désactive
        self.kill_can_interface()

        # Vérifie si le dossier du pilote USB2CAN est présent et le télécharge si nécessaire
        self.download_usb2can_driver()

        # Crée l'interface CAN
        self.create_can_interface()

if __name__ == "__main__":
    can_interface_manager = CANInterfaceManager()
    can_interface_manager.manage_can_interface()
