<h1 align="center">AI Console</h1>

## Running Your AI Console

In order to run your own AI Console:

1. CD into the project folder `/ai-console`
2. Install dependencies `poetry install` and `cd web && yarn`
3. In two distinct terminal windows run: `poetry run backend` and `cd web && yarn dev`

Optionally you can run `poetry run aiconsole` which will spawn two servers, but it's less ideal for development as it's often benefitial to restart just one.

Requires OPENAI_API_KEY env variable to be set.

## Manuals

Create .md files in ./manuals directory in the following format:


```md
<!---
Description of when this manual should be used?
-->

Actual content of a manual
```

Files are monitored and automatically loaded, then used as context. You can keep there API manuals, login information, prompts and other contextual information.

You can see examples of manuals i ./preset/manuals directory

## TODO List - this milestone
- [ ] Setup a package
- [ ] Can not delete messages while new message is being generated
- [ ] Allow to submit a message even if analysis of it is still in progress (it should then wait and send the message when analyis is complete)
- [ ] When analysis is not done, the user should be able to submit the message, it should then get actually submitted when the analysis arrives
- [ ] Errors when context is full
- [ ] Trigger analysis of the message when any of it's parameters change
- [ ] Disallow sending messages when output is being generated
- [ ] Give the ability to select and copy the contents of the messages while a new message is generated (right now each token resets the selection in the browser)
- [x] Rename Knowledge to Manuals - it better suits the thing
- [x] Input box is not shrinking after sending a big multiline message.
- [ ] Input box still sometimes does not shrink ...
- [ ] From frontend: "Stop" button, to cancel all processing and generation. The request to OpenAI API can be forgotten, it does not need to be canceled.
- [x] Wobbly scrolling when new tokens arrive. It should be very smooth and slow. Auto scrolling with new messages should only happen when we are at the bottom of the screen (maybe up to -100px from the bottom).
- [x] Guzik do kasowania messagey na gorze samej (chodzi o przesuniecie aktualnego)
- [ ] Asking the user if the code should be ran on the frontend: Yes | No | Always
- [ ] Editing of current messages (mega potrzebne do przycinania duzych wiadomosci - kontekst szybko wypelniaja)
- [ ] Sometimes the system totally hangs and you can not do CTRL-C even. (Does this happen when command is executed, I seen somthing about it on open-interpreter Discord, is this related: https://github.com/KillianLucas/tokentrim/issues/3 ?)
- [ ] Sometimes CWD / PWD is reset to initial one. Why?
- [ ] Better way to spawn both servers using single command, maybe rewrite "yarn dev" using fast api?
- [ ] How to run it from a different dir? In order to use ./manuals and .aic-XXX from that dir?
- [ ] How to summarize a PDF I have locally without specifying a path in a text form? Drag and drop somewhere? Upload?
- [ ] Hide code and execution in a foldable section similarily to what chatgpt does (advanced data analysis)
- [ ] Context window errors

## TODO List - strech goals
- [ ] Do we need to clean up the repo
- [ ] Settings available to change on the frontend: Automatically Run Code?
- [ ] Display numbers of tokens on hover when hovering on memory (how many used how many in total)
- [ ] Implementation of strategies (MC)
- [ ] Some default manuals and strategies (MC)
- [ ] Implement strategies with each having a seperate system prompt, writing text and code should be different.
- [x] Actually preloaded manuals and strategies should be copied to the current directory if there isn't one already there
- [ ] Randomized samples in materials, eg. have 10 samples of content, and randomly place 5. Automatic inclusions of content?
- [ ] Additional display of memory used in /gpt
- [x] Seperation of Analysis so it can be viewed on the frontend
- [ ] Manual edition of analysis (strategy, manuals etc)
- [ ] Have history side bar showing history, the same as in ChatGPT
- [ ] Backend storage for simulating terminal like behaviour when pressing up arrow (scrolling through history), it works currently only for messages since refresh. (UI already does that)
- [ ] History saving to .aic-history, each chat should be a seperate file. Identifier should be given by frotend. Save only on full messages not on each token.
- [x] Frontend should display somehow what strategy is used and what materials, but it should not keep it within the message history.
- [ ] Console should have the ability to write code that modifies and lists manuals. How to achive that?
- [ ] Console should have the ability to manipulate internal variables like auto accept, debug etc. How to achive that?
- [x] (Manuals) Explore moveing from toml to something more readable, maybe .md?
- [x] Super dynamic materials, their content is instanciated each time seperatelly. Main example is randomisation of content, but could also be something like query based downloading of manuals or even downloading them through API?
- [ ] Various sources of materials, mabe Notion or spreadsheet?
- [ ] Move communicaion to websockets so things can be sent to frontend outside of normal flow (cron activity, errors etc)
- [ ] Ability to choose QUALITY / FAST in the frontend for processing
- [ ] Are we supporting other models that interpreter supports?
- [ ] Show "Mode"
- [ ] Experiment with optimizing with 3.5-turbo
- [ ] Setup on Azure OpenAI service
- [ ] Optimize main loop so less code is pre-generated and duplicated, optimize unnecesary need to prompt console to continue.