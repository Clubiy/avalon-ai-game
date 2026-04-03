# -*- coding: utf-8 -*-
"""Default prompts"""


class EnglishPrompts:
    """English prompts used to guide the Avalon game."""

    to_dead_player = (
        "{}, you're eliminated from the quest. Now you can make a final statement to "
        "all alive players before you leave the game."
    )

    to_all_new_game = (
        "A new game is starting, the players are: {}. Now we randomly "
        "reassign the roles to each player and inform them of their roles "
        "privately."
    )

    to_all_night = (
        "Night has fallen, everyone close your eyes. Evil forces open your "
        "eyes and acknowledge each other..."
    )

    to_wolves_discussion = (
        "[EVIL FORCES ONLY] {}, you should discuss and "
        "decide on a team for the quest. Current alive players "
        "are {}. Remember to set `reach_agreement` to True if you reach an "
        "agreement during the discussion."
    )

    to_wolves_vote = "[EVIL FORCES ONLY] Which players do you propose for the quest?"

    to_wolves_res = (
        "[EVIL FORCES ONLY] The voting result is {}. So you have chosen these players: "
        "{}."
    )

    to_all_witch_turn = (
        "Merlin's turn, Merlin open your eyes and check for evil forces tonight..."
    )
    to_witch_resurrect = (
        "[MERLIN ONLY] {witch_name}, you're Merlin, and you can see the evil forces "
        "except Mordred. The known evil forces are: {dead_name}. Remember to hide "
        "your identity while guiding the loyal servants."
    )

    to_witch_resurrect_no = (
        "[MERLIN ONLY] Merlin has chosen not to reveal information."
    )
    to_witch_resurrect_yes = (
        "[MERLIN ONLY] Merlin has provided information about evil forces."
    )

    to_witch_poison = (
        "[MERLIN ONLY] {witch_name}, as Merlin, you know the evil forces. "
        "Use this knowledge wisely to guide the loyal servants without revealing yourself."
    )

    to_all_seer_turn = (
        "Percival's turn, Percival open your eyes and look for Merlin and Morgana..."
    )

    to_seer = (
        "[PERCIVAL ONLY] {}, as Percival you can see Merlin and Morgana "
        "tonight, but you cannot distinguish them. Who do you want to check? Give me your reason and decision."
    )

    to_seer_result = (
        "[PERCIVAL ONLY] You've checked {agent_name}, and one of them is Merlin/Morgana."
    )

    to_hunter = (
        "[ASSASSIN ONLY] {name}, as the Assassin, after the quests are complete, "
        "you can choose one player to assassinate. Choose carefully - if it's Merlin, "
        "evil wins immediately. Give me your reason and decision."
    )

    to_all_hunter_shoot = (
        "The Assassin has chosen to eliminate {} in the final assassination."
    )

    to_all_day = (
        "Day has come, all players open your eyes. Last night, "
        "the following events occurred: {}."
    )

    to_all_peace = (
        "Day has come, all the players open your eyes. Last night was "
        "peaceful, no special events occurred."
    )

    to_all_discuss = (
        "Now the alive players are {names}. The game goes on, it's time to "
        "discuss and vote on the quest team. Now you each take turns "
        "to speak once in the order of {names}."
    )

    to_all_vote = (
        "Now the discussion is over. Everyone, please vote to approve or reject "
        "the proposed quest team: {}."
    )

    to_all_res = "The voting result is {}. So {} has been approved/rejected."

    to_all_wolf_win = (
        "There are {n_alive} players alive, and {n_werewolves} of them are "
        "evil forces. "
        "The game is over and evil forces win🐺🎉!"
        "In this game, the true roles of all players are: {true_roles}"
    )

    to_all_village_win = (
        "All the evil forces have been identified through successful quests."
        "The game is over and loyal servants win🏘️🎉!"
        "In this game, the true roles of all players are: {true_roles}"
    )

    to_all_continue = "The game goes on."

    to_all_reflect = (
        "The game is over. Now each player can reflect on their performance. "
        "Note each player only has one chance to speak and the reflection is "
        "only visible to themselves."
    )


class ChinesePrompts:
    """Chinese prompts used to guide the Avalon game."""

    to_dead_player = "{}，你从任务中出局了。现在你可以在离开游戏前向所有存活玩家发表最后的声明。"

    to_all_new_game = "新的一局游戏开始，参与玩家包括：{}。现在为每位玩家重新随机分配身份，并私下告知各自身份。"

    to_all_night = "夜幕降临，请所有人闭眼。邪恶势力请睁眼并互相确认..."

    to_wolves_discussion = (
        "[仅邪恶势力可见] {}, 你们可以讨论并决定派哪些玩家执行任务。当前存活玩家有：{}。"
        "如果达成一致，请将 `reach_agreement` 设为 True。"
    )

    to_wolves_vote = "[仅邪恶势力可见] 你提议哪些玩家参加任务？"

    to_wolves_res = "[仅邪恶势力可见] 投票结果为 {}，所以你们选择的玩家是：{}。"

    to_all_witch_turn = "轮到梅林行动，梅林请睁眼并查验邪恶势力..."
    to_witch_resurrect = (
        "[仅梅林可见] {witch_name}，你是梅林，你可以看到除了莫德雷德之外的所有邪恶势力。"
        "已知的邪恶势力有：{dead_name}。记住要在隐藏自己身份的同时引导忠诚仆人。"
    )

    to_witch_resurrect_no = "[仅梅林可见] 梅林选择不透露信息。"
    to_witch_resurrect_yes = "[仅梅林可见] 梅林提供了关于邪恶势力的信息。"

    to_witch_poison = "[仅梅林可见] {witch_name}，作为梅林，你知道邪恶势力的身份。明智地利用这些信息来引导忠诚仆人，不要暴露自己。"

    to_all_seer_turn = "轮到派西维尔行动，派西维尔请睁眼并寻找梅林和莫甘娜..."

    to_seer = "[仅派西维尔可见] {}, 作为派西维尔，你今晚可以看到梅林和莫甘娜，但无法区分他们。你想查验谁？请给出理由和决定。"

    to_seer_result = "[仅派西维尔可见] 你查验了{agent_name}，他们是梅林或莫甘娜其中之一。"

    to_hunter = (
        "[仅刺客可见] {name}，你是刺客，在任务完成后，你可以选择一名玩家进行刺杀。"
        "慎重选择——如果是梅林，邪恶方立即获胜。请给出理由和决定。"
    )

    to_all_hunter_shoot = "刺客选择在最终刺杀中淘汰{}。"

    to_all_day = "天亮了，请所有玩家睁眼。昨晚发生了以下事件：{}。"

    to_all_peace = "天亮了，请所有玩家睁眼。昨晚平安无事，没有特殊事件发生。"

    to_all_discuss = "现在存活玩家有：{names}。游戏继续，大家开始讨论并对任务队伍投票。请按顺序（{names}）依次发言。\n\n重要提示：\n1. 发言时请使用<发言：>标签包裹你要展示的内容，例如：<发言：我认为应该投赞成票>\n2. 绝对不允许暴露自己的真实身份\n3. 可以假装成其他身份来混淆视听\n4. 根据你的角色设定进行推理和发言"

    to_all_vote = "讨论结束。请大家投票赞成或反对提议的任务队伍：{}。"

    to_all_res = "投票结果为 {}，所以{}被通过/否决。"

    to_all_wolf_win = (
        "当前存活玩家共{n_alive}人，其中{n_werewolves}人为邪恶势力。"
        "游戏结束，邪恶势力获胜🐺🎉！"
        "本局所有玩家真实身份为：{true_roles}"
    )

    to_all_village_win = "通过成功完成任务，所有邪恶势力已被识别。游戏结束，忠诚仆人获胜🏘️🎉！本局所有玩家真实身份为：{true_roles}"

    to_all_continue = "游戏继续。"

    to_all_reflect = "游戏结束。现在每位玩家可以对自己的表现进行反思。注意每位玩家只有一次发言机会，且反思内容仅自己可见。"
