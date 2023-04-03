# Learn DiscordWizard: A Comprehensive Guide 📘

Welcome to the LEARN.md guide for DiscordWizard! This guide aims to help you understand the inner workings of DiscordWizard and provide you with the knowledge you need to get started. DiscordWizard not only clones the server structure but also mirrors any changes and messages between the servers.

## Table of Contents

- [Learn DiscordWizard: A Comprehensive Guide 📘](#learn-discordwizard-a-comprehensive-guide-)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Setting up the Environment](#setting-up-the-environment)
  - [Key Components](#key-components)
  - [Working with Websockets](#working-with-websockets)
  - [Understanding Webhooks](#understanding-webhooks)
  - [Comparing Sitemaps](#comparing-sitemaps)
  - [Client and Server Interaction](#client-and-server-interaction)
  - [Mirroring Changes and Messages](#mirroring-changes-and-messages)
  - [Understanding Webhooks](#understanding-webhooks-1)
  - [Troubleshooting Common Issues](#troubleshooting-common-issues)
  - [Further Reading and Resources](#further-reading-and-resources)

## Overview

DiscordWizard is a tool that helps you replicate the structure of a Discord server by creating an identical server layout based on an input server. The project consists of two main parts: a client and a server, which communicate through websockets. It also mirrors any changes and messages in real-time between the two servers.

## Setting up the Environment

1. Install the required packages: `discord.py-self`, `websockets`, and `pyyaml`. Note that the `discord.py-self` package is necessary for this project; you can find it here: https://pypi.org/project/discord.py-self/
2. Create a `settings.yaml` file with the necessary configurations, including the Discord bot tokens and other settings for both the client and the server.
3. Launch the `server.py` and `client.py` scripts.

## Key Components

The DiscordWizard project is split into two main files:

1. **server.py**: This script handles the server-side operations, such as updating the server structure, comparing sitemaps, and saving the sitemap to a file.
2. **client.py**: This script deals with the client-side interactions, such as sending messages to the websocket and sending the sitemap.

## Working with Websockets

DiscordWizard uses websockets to communicate between the client and the server. This is done using the `websockets` library in Python. The `server.py` script sets up a websocket server, while the `client.py` script connects to the websocket server and sends messages or sitemaps as needed.

## Understanding Webhooks

DiscordWizard uses webhooks to send messages between Discord servers. The `server.py` script creates a webhook named "DickNBavs" in each text channel. The webhook URL is then saved in the sitemap file so that the client can use it to send messages.

## Comparing Sitemaps

The `compare_sitemaps` function in `server.py` takes two sitemaps as inputs (an old sitemap and a new one) and compares them. It returns a list of removed channels and a list of title changes (both category and channel title changes).

## Client and Server Interaction

The `client.py` script sends the sitemap to the websocket server, which is handled by the `server.py` script. The `server.py` script then updates the server structure, saves the sitemap, and compares the new sitemap with the old one, printing out any changes.

## Mirroring Changes and Messages

DiscordWizard mirrors any changes in the server structure, as well as messages between the two servers. The `client.py` script listens for new messages and sends them to the websocket server, which in turn sends the
messages to the appropriate channels using webhooks. Similarly, any changes in the server structure are detected and mirrored by updating the sitemap and sending it through the websocket connection.

## Understanding Webhooks

DiscordWizard uses webhooks to send messages between Discord servers. The `server.py` script creates a webhook with the specified name in the `settings.yaml` file (e.g., "DiscordWizard") in each text channel. The webhook URL is then saved in the sitemap file so that the client can use it to send messages.

## Troubleshooting Common Issues

1. **Discord API rate limits**: Discord imposes rate limits on certain actions, such as creating channels or categories. DiscordWizard has implemented asyncio.sleep() to wait between these actions, but you may need to adjust the waiting times based on your specific use case.
2. **Websocket connection issues**: If you experience issues with the websocket connection between the client and server, ensure that both scripts are running and the specified websocket URI is correct.
3. **Configuration errors**: Double-check your `settings.yaml` file for any errors in the token or other configuration settings.

## Further Reading and Resources

1. Discord.py-self: https://pypi.org/project/discord.py-self/
2. Websockets library: https://websockets.readthedocs.io/en/stable/
3. Discord.py documentation: https://discordpy.readthedocs.io/en/stable/
4. Discord Developer Portal: https://discord.com/developers/docs/intro
5. Discord Webhooks Guide: https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks

We hope this guide helps you understand the inner workings of DiscordWizard and provides you with the knowledge you need to get started. If you have any questions or need further assistance, feel free to reach out to the community or consult the resources provided. Happy replicating!
