// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <string>
#include "CoreMinimal.h"
#include "CSVtoTArray.generated.h"

/**
 * 
 */
UCLASS(Blueprintable)
class IKRIG_EXAMPLE_API UCSVtoTArray : public UObject
{
	GENERATED_BODY()

public:
	UCSVtoTArray();
	~UCSVtoTArray();

	UFUNCTION(BlueprintCallable)
		void LoadCSVFile(FString InFilePath, float InFramerate);

	UFUNCTION(BlueprintCallable)
		TArray<float> GetPoseAtTime(float Time);

private:
	std::vector<std::vector<float> > Data;
	float Framerate;
	int NFrames;
	std::string FilePath;
	char Delimeter;

	std::vector<std::vector<float> > GetData();
};
