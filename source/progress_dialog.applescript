#!/usr/bin/env osascript
-- Progress dialog for Cartoonizer startup

on run argv
    set status_text to "Starting up..."
    if (count of argv) > 0 then
        set status_text to item 1 of argv
    end if
    
    display notification status_text with title "Cartoonizer" subtitle "Initializing..."
end run
