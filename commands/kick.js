module.exports = {
    name: 'kick',
    description: "This command kicks a member!",
    execute(message, args) {
        const target = message.mentions.users.first();
        if (target) {
            const memberTarget = message.guild.members.cache.get(target.id);
            memberTarget.kick();
            message.channel.send("хаха-пошол нахуй");
        } else {
            message.channel.send(`не пошол нахуй`);
        }
    }
}