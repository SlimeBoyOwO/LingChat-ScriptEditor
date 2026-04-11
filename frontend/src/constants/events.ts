export const DESCRIPTIONS: Record<string, string> = {
    narration: '添加叙述文本',
    player: '添加玩家对话',
    dialogue: '添加角色对话',
    ai_dialogue: '添加AI生成对话',
    modify_character: '修改角色状态',
    background: '设置背景图片',
    music: '播放背景音乐',
    input: '玩家输入事件',
    choices: '玩家选择事件',
    set_variable: '设置变量值',
    chapter_end: '章节结束/跳转'
}

export interface EventField {
    key: string
    label: string
    type: 'text' | 'number' | 'textarea' | 'select' | 'file'
    options?: string[] // For select
    default?: any
    hint?: string
    resourceType?: 'background' | 'music' | 'character' | 'sound' // For file type - which resource category to use
}

export interface EventSchema {
    type: string
    label: string
    color: string
    mandatory: EventField[]
    optional: EventField[]
}

const COMMON_OPTIONAL: EventField[] = [
    { key: 'condition', label: 'Condition', type: 'text', hint: 'Variable expression (e.g. var > 1)' },
    { key: 'duration', label: 'Duration', type: 'number', default: 0 }
]

export const EVENT_SCHEMAS: Record<string, EventSchema> = {
    // Story Events
    narration: {
        type: 'narration',
        label: 'Narration',
        color: 'border-purple-500/50 bg-purple-900/20',
        mandatory: [
            { key: 'text', label: 'Content', type: 'textarea' }
        ],
        optional: [...COMMON_OPTIONAL]
    },
    player: {
        type: 'player',
        label: 'Player Says',
        color: 'border-gray-500/50 bg-gray-900/20',
        mandatory: [
            { key: 'text', label: 'Content', type: 'textarea' }
        ],
        optional: [...COMMON_OPTIONAL]
    },
    
    // Character Events
    dialogue: {
        type: 'dialogue',
        label: 'Character Dialogue',
        color: 'border-blue-500/50 bg-blue-900/20',
        mandatory: [
            { key: 'character', label: 'Character', type: 'file', resourceType: 'character' },
            { key: 'text', label: 'Content', type: 'textarea' }
        ],
        optional: [...COMMON_OPTIONAL]
    },
    ai_dialogue: {
        type: 'ai_dialogue',
        label: 'AI Dialogue',
        color: 'border-cyan-500/50 bg-cyan-900/20',
        mandatory: [
             { key: 'character', label: 'Character', type: 'file', resourceType: 'character' },
             { key: 'prompt', label: 'AI Prompt', type: 'textarea' }
        ],
        optional: [...COMMON_OPTIONAL]
    },
    modify_character: {
        type: 'modify_character',
        label: 'Modify Character',
        color: 'border-pink-500/50 bg-pink-900/20',
        mandatory: [
            { key: 'action', label: 'Action', type: 'select', options: ['show_character', 'hide_character', 'move_character', 'shake_character'] },
            { key: 'character', label: 'Character', type: 'file', resourceType: 'character' }
        ],
        optional: [
            { key: 'emotion', label: 'Emotion', type: 'text' },
            ...COMMON_OPTIONAL
        ]
    },

    // Assets
    background: {
        type: 'background',
        label: 'Background',
        color: 'border-green-500/50 bg-green-900/20',
        mandatory: [
            { key: 'imagePath', label: 'Image Path', type: 'file', resourceType: 'background' }
        ],
        optional: [...COMMON_OPTIONAL]
    },
    music: {
        type: 'music',
        label: 'Music',
        color: 'border-yellow-500/50 bg-yellow-900/20',
        mandatory: [
            { key: 'musicPath', label: 'Music Path', type: 'file', resourceType: 'music' }
        ],
        optional: [...COMMON_OPTIONAL]
    },

    // Input
    input: {
        type: 'input',
        label: 'Input',
        color: 'border-orange-500/50 bg-orange-900/20',
        mandatory: [
            { key: 'hint', label: 'Hint', type: 'text', hint: 'Prompt text for player input' }
        ],
        optional: [...COMMON_OPTIONAL]
    },

    // Choices
    choices: {
        type: 'choices',
        label: 'Choices',
        color: 'border-indigo-500/50 bg-indigo-900/20',
        mandatory: [
            { key: 'options', label: 'Options', type: 'textarea', hint: 'List of choice options with text and actions' },
            { key: 'allow_free', label: 'Allow Free Input', type: 'text', hint: 'Set to "true" to allow custom input', default: false }
        ],
        optional: [...COMMON_OPTIONAL]
    },

    // Logic
    set_variable: {
        type: 'set_variable',
        label: 'Set Variable',
        color: 'border-red-500/50 bg-red-900/20',
        mandatory: [
            { key: 'name', label: 'Variable Name', type: 'text' },
            { key: 'value', label: 'Value', type: 'text' }
        ],
        optional: [...COMMON_OPTIONAL]
    },
    chapter_end: {
        type: 'chapter_end',
        label: 'Chapter End',
        color: 'border-white/50 bg-white/10',
        mandatory: [
            { key: 'end_type', label: 'End Type', type: 'select', options: ['linear', 'branching', 'ai_judged'], default: 'linear' },
            { key: 'next_chapter', label: 'Next Chapter', type: 'text', hint: 'Chapter path or "end"' }
        ],
        optional: [
            { key: 'options', label: 'Options', type: 'textarea', hint: 'For branching/ai_judged: list of options with actions' },
            ...COMMON_OPTIONAL
        ]
    }
}
