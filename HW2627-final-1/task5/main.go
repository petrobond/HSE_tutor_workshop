// Задание 5. Максимум из N чисел
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

		var maxVal, minVal int
		for i := 1; i <= n; i++ {
			x := readInt(fmt.Sprintf("Введите число %d: ", i))

			if i == 1 || x > maxVal {
				maxVal = x
			}
			if i == 1 || x < minVal {
				minVal = x
			}
		}

		fmt.Printf("Максимальное значение: %d\n", maxVal)
		fmt.Printf("Минимальное значение: %d\n", minVal)

		fmt.Print("Повторить? (д/н): ")
		var answer string
		fmt.Scan(&answer)
		if answer != "д" {
			break
		}
		fmt.Println()
	}
}
