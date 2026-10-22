async def has_role(interaction, role_name="Quote Manager"):
    return any(role.name == role_name for role in interaction.user.roles)