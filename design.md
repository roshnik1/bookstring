# Ben's Current Design Thoughts


# Concepts

## Indexed
Something that is indexed has a stable UUID reference and can be looked up by that reference (regardless of type). Lots of things can be indexed including books, book series, chapters, and authors.

## Space
A space is a communication area centered around something indexed. You can think of this as being like a post on a forum like Reddit. Messages can be added directly under a space.

Ordering of messages under a space is user-controlled, probably with 'top karma' being the default.

## Node
A node is a comment that's the root of a thread. Once a message becomes a node its structure changes; edits are made as atomic messages within the underlying thread (like how 'glue' proposes chat document editing). Nodes can receive votes that will generate karma.

The idea with a node is that it should become a document reflecting the discussion taking place underneath. Ideally a space should have top-level messages that are mostly nodes summarizing the discussion threads that spawn under them.

## Thread
A thread is a live chat interface that shows the most recently sent messages at the bottom. Any message in a thread can become a node with a new thread branching off from it. There is no nesting limit for threads.

Threads can also be spawned from marks and taggings.

### Hoisting
If an important node within a thread is relevant to the higher-level discussion it can be 'hoisted' up a level so it is visible at that higher level.

## Quote
Messages and books can both be quoted, where a quote contains all of the information needed to find the exact string of text in the quote. Quotes cannot be indexed but they can be marked.

## Mark
A mark is a reaction to a message or quote. Marks can include things like up-voting/down-voting, spoiler tagging, or other reactions. Users can mark their own messages (though doing so will not affect their karma) to mark spoilers or add asides.

Marks are public and may include a message explaining their reasoning or adding context.

Once a mark is made other users can agree/disagree with the mark (also public), optionally adding their own thoughts to the mark.

### Spoilers
A central feature of Bookstring is allowing users to track their progress reading a work. One benefit of this is that spoilers can be masked automatically. If you've read a book to chapter three you should be able to block everything from chapter four onward and read discussions about the first three chapters without fear.

This means we want to make it easy to mark spoilers within a message.

### Voting

## Tag
A tag is a small string that can be applied to anything indexed, tags themselves are also indexed which means tags can apply to tags. However, to limit ontological runaway we limit this to three levels: base tags (applied to non-tag indexes), organization tags (applied to base tags), and meta tags (applied to organization or other meta tags).

A _tagging_ is the application of a tag to an indexed item. Tagging is public, may be accompanied by a message, and may be the root of a thread. A tagging may be voted on with agree/disagree for whether the tag is relevant.

### Base Tags

### Organization Tags

### Meta Tags


## Community
A community is a collection of users organized around a topic.

## Cohort