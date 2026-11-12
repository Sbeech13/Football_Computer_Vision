%% Distance to Ball Analysis
% Trial summary (mean + SD distance) + per-second summary (mean + SD)
clc; clear; close all;

%% Participant list
dataFiles = ["This should be a list of all of your datafiles"];
folderPath = 'Data/';

%% Load Ball coordinates
ballFolder = 'Ball_Outputs/';
fps = 30;

% Container that associates each video number with its file
ballFiles = containers.Map( ...
    [1, 2, 3, 4], ...
    { ...
    "This is the list of CSV outputs for the ball tracker" });

Ball = cell(4,1);
for v = 1:4
    ballFile = fullfile(ballFolder, ballFiles(v));
    
    if ~isfile(ballFile)
        error('Ball file not found: %s', ballFile);
    end
    
    T = readtable(ballFile);
    
    % Frame → time in milliseconds from start of video
    Ball{v}.time = (T.Frame - 1) / fps * 1000; % ms
    Ball{v}.x = T.X;
    Ball{v}.y = T.Y;
    
    fprintf('Loaded video %d: %s (%d frames)\n', v, ballFiles(v), height(T));
end

%% Output tables
TrialSummary = table();
SecondSummary = table();

%% Main loop over participants
for i = 1:numel(dataFiles)
    
    fileName = fullfile(folderPath, dataFiles(i));
    edfData = Edf2Mat(char(fileName));
    fprintf('Processing %s\n', dataFiles(i));
    
    participantID = sscanf(dataFiles(i), '%d');
    
    %% Trial boundaries
    time = edfData.Samples.time;
    posX = edfData.Samples.posX;
    posY = edfData.Samples.posY;
    
    startTimes = edfData.Events.Start.time;
    msgTimes = edfData.Events.Messages.time;
    msgText = edfData.Events.Messages.info;
    stopIdx = find(contains(msgText, 'APLAYSTOP'));
    assert(numel(stopIdx) == 4, 'Expected four APLAYSTOP messages.');
    endTimes = msgTimes(stopIdx);
    
    %% Metadata
    messages = edfData.Events.Messages.info;
    videoMessages = messages(contains(messages, "videonumber"));
    trialMessages = messages(contains(messages, "trialtype"));
    listMessages = messages(contains(messages, "list"));
    
    assert(numel(videoMessages) == 4, 'Expected four video messages.');
    
    videoNumber = zeros(4,1);
    trialType = cell(4,1);
    listType = cell(4,1);
    
    for t = 1:4
        videoNumber(t) = sscanf(videoMessages{t}, '!V TRIAL_VAR videonumber %d');
        trialType{t} = sscanf(trialMessages{t}, '!V TRIAL_VAR trialtype %s');
        listType{t} = sscanf(listMessages{t}, '!V TRIAL_VAR list %s');
    end
    
    %% Process each trial
    for t = 1:4
        
        % Gaze samples for this trial
        idx = time >= startTimes(t) & time <= endTimes(t);
        gazeTime = time(idx) - startTimes(t);
        gazeX = posX(idx);
        gazeY = posY(idx);
        
        v = videoNumber(t); % 1–4
        
        % Interpolate ball position to every gaze sample
        ballX_interp = interp1(Ball{v}.time, Ball{v}.x, gazeTime, 'linear', 'extrap');
        ballY_interp = interp1(Ball{v}.time, Ball{v}.y, gazeTime, 'linear', 'extrap');
        
        % Distance in pixels
        distance = sqrt( (gazeX - ballX_interp).^2 + (gazeY - ballY_interp).^2 );
        
        % ConditionE (C vs E)
        condE = trialType{t};
        if ~strcmp(condE, 'C')
            condE = 'E';
        end
        
        % ----- Trial summary (mean + SD) -----
        meanDist = mean(distance, 'omitnan');
        sdDist   = std(distance, 'omitnan');
        
        newTrialRow = table( ...
            participantID, t, v, ...
            string(trialType{t}), string(condE), string(listType{t}), ...
            meanDist, sdDist, ...
            'VariableNames', { ...
            'Participant','Trial','Video',...
            'Condition','ConditionE','List',...
            'MeanDistanceToBall','SDDistanceToBall'});
        
        TrialSummary = [TrialSummary; newTrialRow];
        
        % ----- Per-second summary (mean + SD) -----
        nSeconds = floor(gazeTime(end)/1000);
        
        for sec = 1:nSeconds
            timeIdx = gazeTime >= (sec-1)*1000 & gazeTime < sec*1000;
            
            if any(timeIdx)
                meanDistSec = mean(distance(timeIdx), 'omitnan');
                sdDistSec   = std(distance(timeIdx), 'omitnan');
            else
                meanDistSec = NaN;
                sdDistSec   = NaN;
            end
            
            newSecRow = table( ...
                participantID, t, v, ...
                string(trialType{t}), string(condE), string(listType{t}), ...
                sec, meanDistSec, sdDistSec, ...
                'VariableNames', { ...
                'Participant','Trial','Video',...
                'Condition','ConditionE','List',...
                'Second','MeanDistanceToBall','SDDistanceToBall'});
            
            SecondSummary = [SecondSummary; newSecRow];
        end
    end
end

%% Save
saveToFile = 1;
if saveToFile == 1
    writetable(TrialSummary, 'DistanceToBall_TrialSummary.csv');
    writetable(SecondSummary, 'DistanceToBall_PerSecond.csv');
end

fprintf('\nFinished.\n');
fprintf(' Trial summary → DistanceToBall_TrialSummary.csv\n');
fprintf(' Per-second   → DistanceToBall_PerSecond.csv\n');