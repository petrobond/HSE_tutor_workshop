// Задание 2. Анализ числа
package main

import (
	"fmt"
	"os"
	"strconv"
)

func readInt(prompt string) int {
	for {
		fmt.Print(prompt)
		var s string
		if _, err := fmt.Scan(&s); err != nil {
			fmt.Println("Ошибка: не удалось прочитать ввод")
			os.Exit(1)
		}
		x, err := strconv.Atoi(s)
		if err != nil {
			fmt.Println("Ошибка: нужно ввести целое число")
			continue
		}
		return x
	}
}

func main() {
	for {
		n := readInt("Введите число N: ")

		if n > 0 {
			fmt.Println("Число положительное")
		} else if n < 0 {
			fmt.Println("Число отрицательное")
		} else {
			fmt.Println("Число равно нулю")
		}

		if n%2 == 0 {
			fmt.Println("Число чётное")
		} else {
			fmt.Println("Число нечётное")
		}

		if n%3 == 0 {
			fmt.Println("Делится на 3")
		} else {
			fmt.Println("Не делится на 3")
		}

		if n%5 == 0 {
			fmt.Println("Делится на 5")
		} else {
			fmt.Println("Не делится на 5")
		}

		if n%3 == 0 && n%5 == 0 {
			fmt.Println("Делится на 3 и на 5 одновременно")
		} else {
			fmt.Println("Не делится на 3 и на 5 одновременно")
		}

		fmt.Print("Повторить? (д/н): ")
		var answer string
		fmt.Scan(&answer)
		if answer != "д" {
			break
		}
		fmt.Println()
	}
}
