from constants import Lang, Str_Dict_Keys

def get_locale(language, key, *args):
  string_dict = {
    Lang.JP : {
      Str_Dict_Keys.ALL : '全ボイスチャンネル',
      Str_Dict_Keys.DEFAULT : '設定されていないボイスチャンネル',
      Str_Dict_Keys.ALERT : '【{}】：{}人',
      Str_Dict_Keys.ALERT_NAME_JOIN : '{}が【{}】に入室しました：{}人',
      Str_Dict_Keys.ALERT_NAME_LEAVE : '{}が【{}】から退室しました：{}人',
      Str_Dict_Keys.MY_NOTICE : '<@{}> あなたの入退室に関する通知が{}になりました',
      Str_Dict_Keys.SEND_HERE : '{}の通知先を【{}】に変更しました。',
      Str_Dict_Keys.LANG_CHANGED : '日本語に変更しました。',
      Str_Dict_Keys.VC_CHANGED : '【{}】の入退室通知が{}になりました。',
      Str_Dict_Keys.NOTICE_TYPE_CHANGED : 'ユーザー名の通知が{}になりました。',
      Str_Dict_Keys.NOT_INTEGER : 'ボイスチャンネルまたはステージチャンネルを右クリック／長押しした後「IDをコピー」を選択して貼り付けてください。',
      Str_Dict_Keys.NO_CHANNEL : 'ボイスチャンネルまたはステージチャンネルが存在しません。IDを確認してください。',
      Str_Dict_Keys.NO_PERMISSIONS : '実行には管理者権限が必要です。',
      Str_Dict_Keys.HELP_MY_NOTICE : 'コマンドを入力したユーザーについて入退室通知のOn/Offを切り替えます。',
      Str_Dict_Keys.HELP_VC_NOTICE : '選択したチャンネルについて入退室通知のOn/Offを切り替えます（管理者限定）。',
      Str_Dict_Keys.HELP_SEND_HERE : 'コマンドを入力したテキストチャンネルを通知先として設定します（管理者限定）。',
      Str_Dict_Keys.HELP_NOTIFY_NAME : '入退室通知にユーザー名を表示するか設定します（管理者限定）。',
      Str_Dict_Keys.HELP_LANG : '言語を切り替えます（管理者限定）。\nSwitch languages. Administrator permissons are required.'
    },
    Lang.EN : {
      Str_Dict_Keys.ALL : 'All VCs',
      Str_Dict_Keys.DEFAULT : 'Unspecified VCs',
      Str_Dict_Keys.ALERT : '{} in \"{}\"',
      Str_Dict_Keys.ALERT_NAME_JOIN : '{} has joined \"{}\": {} in total',
      Str_Dict_Keys.ALERT_NAME_LEAVE : '{} has left \"{}\": {} in total',
      Str_Dict_Keys.MY_NOTICE : '<@{}> Notifications about you are turned {}.',
      Str_Dict_Keys.SEND_HERE : 'Notifications of \"{}\" will be on \"{}\".',
      Str_Dict_Keys.LANG_CHANGED : 'Switched to English.',
      Str_Dict_Keys.VC_CHANGED : 'Notifications of \"{}\" channel are turned {}.',
      Str_Dict_Keys.NOTICE_TYPE_CHANGED : 'Display of user names in notifications is turned {}',
      Str_Dict_Keys.NOT_INTEGER : 'Right-click/long-press on a voice or stage channel, then select \"Copy ID\" and paste it.',
      Str_Dict_Keys.NO_CHANNEL : 'The voice or stage channel does not exist. Please check ID again.',
      Str_Dict_Keys.NO_PERMISSIONS : 'Administrator permissons are required.',
      Str_Dict_Keys.HELP_MY_NOTICE : 'Turn on/off notifications about entry and exit of the user who entered the command.',
      Str_Dict_Keys.HELP_VC_NOTICE : 'Select the voice or stage channel to turn notifications on/off. Administrator permissons are required.',
      Str_Dict_Keys.HELP_SEND_HERE : 'Notifications will be on the text channel where this command is entered. Administrator permissons are required.',
      Str_Dict_Keys.HELP_NOTIFY_NAME : 'Turn display of user names in notifications on/off. Administrator permissons are required.',
      Str_Dict_Keys.HELP_LANG : 'Switch languages. Administrator permissons are required.\n言語を切り替えます（管理者限定）。'
    }
  }
  if (language == Lang.EN) and (key == Str_Dict_Keys.ALERT):
    return string_dict[language][key].format(args[1], args[0])
  elif not args:
    return string_dict[language][key]
  else:
    return string_dict[language][key].format(*args)