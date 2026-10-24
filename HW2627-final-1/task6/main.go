// Задание 6. Количество положительных и отрицательных чисел
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
		n := readInt("Сколько чисел будете вводить: ")

		if n <= 0 {
			fmt.Println("Ошибка: количество чисел должно быть больше нуля")
			continue
		}

		positive, negative, zeros := 0, 0, 0
		for i := 1; i <= n; i++ {
			x := readInt(fmt.Sprintf("Введите число %d: ", i))

			if x > 0 {
				positive++
			} else if x < 0 {
				negative++
			} else {
				zeros++
			}
		}

		fmt.Printf("Положительных чисел: %d\n", positive)
		fmt.Printf("Отрицательных чисел: %d\n", negative)
		fmt.Printf("Нулей: %d\n", zeros)

		fmt.Print("Повторить? (д/н): ")
		var answer string
		fmt.Scan(&answer)
		if answer != "д" {
			break
		}
		fmt.Println()
	}
}
