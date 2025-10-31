interface ParsedDocument {
    rels: Rels;
    "rel-urls": RelUrls;
    items: MicroformatRoot[];
}
type MicroformatProperties = Record<string, MicroformatProperty[]>;
interface MicroformatRoot {
    id?: string;
    lang?: string;
    type?: string[];
    properties: MicroformatProperties;
    children?: MicroformatRoot[];
    value?: MicroformatProperty;
}
interface Image {
    alt: string;
    value?: string;
}
interface Html {
    html: string;
    value: string;
    lang?: string;
}
type MicroformatProperty = MicroformatRoot | Image | Html | string;
type Rels = Record<string, string[]>;
type RelUrls = Record<string, {
    rels: string[];
    text: string;
    title?: string;
    media?: string;
    hreflang?: string;
    type?: string;
}>;
