# DiscordWizard: Your Portal to Discord Server Replication 🧙‍♂️

Welcome to the world of DiscordWizard, your trusty ally for cloning entire Discord servers. With its unique and efficient powers, DiscordWizard will help you mirror a Discord server in no time.

![DiscordWizard: The Ultimate Replicator](https://i.imgur.com/0s4UXzP.png)

To work with DiscordWizard, you'll need:
- The token of a Discord account that is a member of the server you wish to copy
- A target server where the messages will be replicated, along with the token of an account with administrative privileges
- That's it! You're ready to go.

## How DiscordWizard Works 🎩

DiscordWizard operates by having the account in the source server monitor changes and new messages using a websocket. The target account then replicates these changes, creating categories, channels, and even renaming them as needed. Messages are sent through webhooks, ensuring a seamless connection between servers.

To set up DiscordWizard, configure the `settings.yaml` file as shown:

```yaml
client:
  token: "" # Token of the account in the server to be mirrored
  server_id: 1076897222881707200 # Server ID
  excluded_channels:
    - 0 # List of excluded channels, if any
  regex_filter: "(badword1|badword2)" # Regex to block forwarding of messages based on it

server:
  token: "" # Administrator token within your server
  server_id: 1092211111969689751 # Your server ID
  interval: 60 # Delay in seconds between interactions with Discord APIs to create channels/webhooks/categories
  webhook_name: "DickNBalls" # Webhook name to use
  websocket:
    port: 8080 # Port to use
    host: "localhost" # Host to use
```
Additionally, you can use the `proxies.txt` file to provide a list of proxies to prevent hitting Discord rate limits when mirroring large servers with high message volume. List one proxy per line in the format `ip:port:user:pass` or `ip:port`.

To start the server, run:
```bash
python3 server.py
```
To launch the client, execute:
```bash
python3 client.py
```
And just like that, the replication begins! 🎉

DiscordWizard separates the client and server into two different scripts. This versatile design allows you to mirror multiple source servers (clients) to the same target server, broadening your possibilities and streamlining the process.

*Note*: The first time you run DiscordWizard, it will create channels, categories, and webhooks. This may take a moment due to Discord's rate limit restrictions. For larger servers, use a higher interval (40/60) to avoid hitting Discord's rate limits.

## How to Contribute 🤝

We welcome and appreciate contributions from the community! If you'd like to contribute to DiscordWizard, here's how you can get involved:

1. **Fork the repository**: Click the 'Fork' button at the top-right corner of the main GitHub page to create your own copy of the repository.

2. **Clone your fork**: Clone your forked repository to your local machine using `git clone https://github.com/YOUR-USERNAME/DiscordWizard.git`.

3. **Create a branch**: Before making any changes, create a new branch for your contribution using `git checkout -b your-feature-branch`.

4. **Make changes**: Implement your feature, fix bugs, or make other improvements to the code.

5. **Commit and push**: Commit your changes and push them to your forked repository using `git commit -m "Your commit message"` followed by `git push origin your-feature-branch`.

6. **Create a pull request**: On the GitHub page of your forked repository, click the 'Compare & pull request' button to submit your changes for review. Provide a clear description of your changes and any additional information that may be helpful.

7. **Stay involved**: Keep an eye on your pull request and be ready to respond to feedback, make changes, or answer questions. Your active participation is crucial for a smooth review process.

By following these steps, you can contribute to the development of DiscordWizard and help make it even better for everyone! We look forward to collaborating with you. 🚀

## Connect with the Developer 🚀

Stay connected and keep up with ongoing projects and innovations.

💌 For questions or feedback, feel free to reach out via email at [glizzykingdreko@protonmail.com](mailto:glizzykingdreko@protonmail.com).

🐦 Follow on Twitter for updates and insights at [@glizzykingdreko](https://twitter.com/glizzykingdreko).

📚 Read more about work on Medium by visiting [medium.com/@glizzykingdreko](https://medium.com/@glizzykingdreko).

🔮 Explore code repositories on GitHub at [github.com/glizzykingdreko](https://github.com/glizzykingdreko).

Join the journey and make your Discord server replication experience a breeze! 🎉
