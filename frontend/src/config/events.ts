export interface EventField {
    key: string
    label: string
    type: 'text' | 'number' | 'textarea' | 'select' | 'file'
    options?: string[] // For select
    default?: any
    hint?: string
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
            { key: 'character', label: 'Character', type: 'text' },
            { key: 'text', label: 'Content', type: 'textarea' }
        ],
        optional: [...COMMON_OPTIONAL]
    },
    ai_dialogue: {
        type: 'ai_dialogue',
        label: 'AI Dialogue',
        color: 'border-cyan-500/50 bg-cyan-900/20',
        mandatory: [
             { key: 'character', label: 'Character', type: 'text' },
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
            { key: 'character', label: 'Character', type: 'text' }
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
            { key: 'imagePath', label: 'Image Path', type: 'file' }
        ],
        optional: [...COMMON_OPTIONAL]
    },
    music: {
        type: 'music',
        label: 'Music',
        color: 'border-yellow-500/50 bg-yellow-900/20',
        mandatory: [
            { key: 'musicPath', label: 'Music Path', type: 'file' }
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
    end: {
        type: 'end',
        label: 'End / Jump',
        color: 'border-white/50 bg-white/10',
        mandatory: [],
        optional: [
            { key: 'next', label: 'Next Chapter', type: 'text', hint: 'Chapter path or "end"' },
            { key: 'condition', label: 'Condition', type: 'text' }
        ]
    }
}
