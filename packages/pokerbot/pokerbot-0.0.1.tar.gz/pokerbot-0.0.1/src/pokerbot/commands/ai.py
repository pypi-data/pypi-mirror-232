def ai_run(state={}, interactive=False, learn_spanish=False):
    from pokerbot import Console
    from pokerbot.ai import bot
    from pokerbot.systems import LearnSpanishSystem

    if learn_spanish:
        bot.ai.additional_prompts.append(LearnSpanishSystem())

    console = Console()
    console.print(f"pokerbot.ai: ", style="bold violet blink")
    console.print(f"access to: {bot.name}")
    console.print(f"state: {state}")

    if interactive:
        import ibis
        import IPython

        from rich import print

        from pokerbot.tools.birdbrain import con, tables

        ibis.options.interactive = True

        IPython.embed(colors="neutral")
