from os import system, environ, popen


class LavalinkBootstrap:
    def __init__(self):
        """Gets latest build number and sets config variables in application.yml"""

        self._version_number = self.prepare_version_number()

        self.download_command = f"curl -L https://ci.fredboat.com/repository/download/Lavalink_Build/{self._version_number}/Lavalink.jar?guest=1 -O"
        print(f"[INFO] Download command: {self.download_command}")

        self.replace_port_command = 'sed -i "s|DYNAMICPORT|$PORT|" application.yml'
        self.replace_password_command = 'sed -i "s|DYNAMICPASSWORD|$PASSWORD|" application.yml'
        self.replace_password_command_no_password = 'sed -i "s|DYNAMICPASSWORD|youshallnotpass|" application.yml'

        # Heroku provides basic Java configuration based on dyno size, no need in limiting memory
        self._additional_options = environ.get("ADDITIONAL_JAVA_OPTIONS")

        # User-provided config, will override heroku's
        self.run_command = f"java -jar Lavalink.jar {self._additional_options}"


    def prepare_version_number(self):
        """Gets latest build number the lavalink ci"""

        builds = (
            popen(
                f"""curl --silent https://ci.fredboat.com/repository/download/Lavalink_Build/?guest=1"""
            )
            .read()
            .strip()
            # removing HTML stuff
            .replace("https://ci.fredboat.com/repository/download/Lavalink_Build/", "")
            .replace("</a><br>", "")
            .split("\n<a href=")
        )

        build = builds[1][builds[1].find(">") + 1 :] #getting latest build
        return build


    def replace_password_and_port(self):
        """Replacing password and port in application.yml"""

        print("[INFO] Replacing port...")

        try:
            system(self.replace_port_command)

            if not environ.get("PASSWORD"):
                print(
                    """
                    [WARNING] You have not specified your Lavalink password in config vars. To do this, go to settings and set the PASSWORD environment variable
                    """
                )
                return system(self.replace_password_command_no_password)

            system(self.replace_password_command)

        except BaseException as exc:
            print(f"[ERROR] Failed to replace port/password. Info: {exc}")

        else:
            print("[INFO] Done. Config is ready now")


    def download(self):
        """Downloads latest release of Lavalink"""

        print("[INFO] Downloading latest release of Lavalink...")

        try:
            system(self.download_command)

        except BaseException as exc:
            print(f"[ERROR] Lavalink download failed. Info: {exc}")

        else:
            print("[INFO] Lavalink download OK")


    def run(self):
        """Runs Lavalink instance"""

        self.download()
        self.replace_password_and_port()

        print("[INFO] Starting Lavalink...")

        try:
            system(self.run_command)
        except BaseException as exc:
            print(f"[ERROR] Failed to start Lavalink. Info: {exc}")


if __name__ == "__main__":
    """Starts our instance"""

    LavalinkBootstrap().run()
