// Fill out your copyright notice in the Description page of Project Settings.

#include "CSVtoTArray.h"
#include "CoreMinimal.h"
#include <vector>
#include <string>
#include <algorithm>
#include <sstream>

UCSVtoTArray::UCSVtoTArray()
{
	FilePath = "D:/OneDrive/Repos/CMU_ikrigv2_csv/93_01.csv";
	Delimeter = ' ';
	Data = GetData();
	Framerate = 15;
	NFrames = Data.size();
}

UCSVtoTArray::~UCSVtoTArray()
{
}

void UCSVtoTArray::LoadCSVFile(FString InFilePath, float InFramerate)
{
	FilePath = TCHAR_TO_UTF8(*InFilePath);
	Delimeter = ' ';
	Data = GetData();
	Framerate = InFramerate;
	NFrames = Data.size();
}

std::vector<std::vector<float> > UCSVtoTArray::GetData()
{
	std::ifstream file(FilePath);
	if (file.is_open()) {
		UE_LOG(LogTemp, Log, TEXT("CSV file has been read properly"));
	}
	else {
		UE_LOG(LogTemp, Log, TEXT("Error reading CSV file"));
	}

	std::vector<std::vector<float> > data;

	std::string line = "";
	// Iterate through each line and split the content using delimeter
	while (getline(file, line))
	{
		std::vector<float> vec;
		std::stringstream ss(line);
		std::string token;
		while (getline(ss, token, Delimeter)) {
			float value = std::stof(token);
			vec.push_back(value);
		}
		data.push_back(vec);
	}
	// Close the File
	file.close();

	return data;
}

TArray<float> UCSVtoTArray::GetPoseAtTime(float Time)
{
	int FrameContinuous, FrameLoop;
	FrameContinuous = static_cast<int>(Time*Framerate);
	FrameLoop = FrameContinuous % NFrames;
	std::vector<float> vec = Data[FrameLoop];
	TArray<float> arr;
	arr.SetNumUninitialized(vec.size());
	for (int i = 0; i < vec.size(); i++) {
		arr[i] = vec[i];
	}
	return arr;
}