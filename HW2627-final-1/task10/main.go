// Задание 10. Статистика последовательности
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

		sum := 0
		even, odd := 0, 0
		var maxVal, minVal int

		for i := 1; i <= n; i++ {
			x := readInt(fmt.Sprintf("Введите число %d: ", i))

			sum += x
			if x%2 == 0 {
				even++
			} else {
				odd++
			}

			if i == 1 || x > maxVal {
				maxVal = x
			}
			if i == 1 || x < minVal {
				minVal = x
			}
		}

		fmt.Printf("Сумма: %d\n", sum)
		fmt.Printf("Среднее значение: %.2f\n", float64(sum)/float64(n))
		fmt.Printf("Максимальное значение: %d\n", maxVal)
		fmt.Printf("Минимальное значение: %d\n", minVal)
		fmt.Printf("Чётных чисел: %d\n", even)
		fmt.Printf("Нечётных чисел: %d\n", odd)

		fmt.Print("Повторить? (д/н): ")
		var answer string
		fmt.Scan(&answer)
		if answer != "д" {
			break
		}
		fmt.Println()
	}
}
