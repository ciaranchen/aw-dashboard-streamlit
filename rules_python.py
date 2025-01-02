class Rules:
    @staticmethod
    def rule_work(data):
        return data['data'].str.contains('豆包|github|gitlab|gogs|jetbrains|Code\\.exe|terminal|PowerShell', regex=True,
                                         case=False)

    @staticmethod
    def rule_programming(data):
        return data['data'].str.contains('Stack Overflow|vim|CSDN博客|开发者工具|jetbrains|webstorm', regex=True,
                                         case=False)

    @staticmethod
    def rule_activitywatch(data):
        return data['data'].str.contains('ActivityWatch|aw-', regex=True, case=False)

    @staticmethod
    def rule_personalproject(data):
        return data['data'].str.contains('conf_root|ConfRoot|FineCache|dotfiles|TabSwitcher|CacheFunc', regex=True,
                                         case=False)

    @staticmethod
    def rule_gateway(data):
        return data['data'].str.contains('Gateway|Fedwork|Zotero', regex=True, case=False)

    @staticmethod
    def rule_referenceprojects(data):
        return data['data'].str.contains('FedE|FedR', regex=True, case=False)

    @staticmethod
    def rule_notes(data):
        return data['data'].str.contains('SiYuan', regex=True, case=False)

    @staticmethod
    def rule_maintain(data):
        return data['data'].str.contains('ciaran_personal\.kdbx', regex=True, case=False)

    @staticmethod
    def rule_software(data):
        return data['data'].str.contains('UniGetUI', regex=True, case=False)

    @staticmethod
    def rule_route(data):
        return data['data'].str.contains('OpenWrt|OpenClash', regex=True, case=False)

    @staticmethod
    def rule_games(data):
        return data['data'].str.contains('Minecraft|Steam', regex=True, case=False)

    @staticmethod
    def rule_video(data):
        return data['data'].str.contains('BiliBili', regex=True, case=False)

    @staticmethod
    def rule_socialmedia(data):
        return data['data'].str.contains('Telegram\.exe', regex=True, case=False)

    @staticmethod
    def rule_music(data):
        return data['data'].str.contains('Spotify|Deezer', regex=True, case=False)

    @staticmethod
    def rule_vr(data):
        return data['data'].str.contains('SideQuest', regex=True, case=False)

    @staticmethod
    def rule_im(data):
        return data['data'].str.contains('QQ|Slack|微信', regex=True, case=False)

    @staticmethod
    def rule_email(data):
        return data['data'].str.contains('Gmail', regex=True, case=False)
