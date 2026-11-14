# Naming conventions

## Scope

ForgeOS naming preferences apply only to the AI engineering organization's own files and directories. They do not apply to the application source code of projects that ForgeOS works on.

## ForgeOS organization files

Use lowercase names and kebab-case for compound names when the relevant tool supports them. This convention covers:

- AI configuration under `.codex/`;
- Claude Code configuration under `.claude/`;
- agent definition files;
- Skills under `.agents/skills/`;
- technology profiles under `profiles/`;
- internal standards, procedures, and workflows;
- installer ownership state under `.forgeos/`;
- ForgeOS-specific documentation.

Tool-required names take precedence over this preference. Use the exact canonical names `AGENTS.md` and `SKILL.md` for shared project instructions and Skill manifests, and `CLAUDE.md` plus `settings.json` for the Claude Code adapter. Claude subagent filenames use lowercase kebab-case with the `.md` extension.

## Software project files

Never impose the ForgeOS kebab-case preference on application source code. For every target project, follow this order of precedence:

1. official language conventions;
2. official framework conventions;
3. conventions already established in the project;
4. local linting and formatting rules.

Examples include `UserController.php` and Laravel migration conventions for Laravel, `getUserProfile()` for PHP, `UserProfile.tsx` for React, `page.tsx` and `layout.tsx` for Next.js, `CustomButton.tsx` for Expo, and `user_service.py` for Python.

Do not rename application files solely to make them conform to ForgeOS naming preferences. Any application rename must instead be justified by the target project's own conventions or by an explicit task requirement.
