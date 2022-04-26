const Discord = require('discord.js');

const client = new Discord.client();

const prefix = "-";

const fs = require('fs');

client.commands = new Discord.Collection();

const commandFiles = fs.readdirSync('./commands/').filter(file => file.endsWith('.js'));
for (const file of commandFiles) {
    const command = require('./commands/${file}');

    client.commands.set(command.name, command);
}

client.on('ready', () => {
});

client.on('message', message => {
    if (!message.content.startsWith(prefix) || message.author.bot) return;
    const args = message.content.slice(prefix.length).split(/+/);
    const command = args.shift().toLowerCase();
    if (command === 'clear') {
        client.commands.get('clear').execute(message, args);
    } else if (command === 'kick') {
        client.commands.get('kick').execute(message, args);
    }

});
client.login('ODg5NTE5NzMwNzYxODAxNzk4.YUibzg.LL1fyAVIwEd5XmIkrnoACjpYaHU');